#!/usr/bin/env python3
"""
Technology Risk Register - Risk Loading Tool

A configurable script to load technology risks into the Risk Register system.
Supports both local development and deployed GCP environments.

Usage:
    python load_risks.py --local                    # Load to localhost:8080
    python load_risks.py --prod                     # Load to GCP endpoint
    python load_risks.py --api-url <custom-url>     # Load to custom endpoint
    python load_risks.py --prod --dry-run           # Validate without posting
    python load_risks.py --local --risk-ids TR-2025-001,TR-2025-002  # Load specific risks
    python load_risks.py --prod --force-update      # Always update existing risks
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Configuration
DEFAULT_LOCAL_URL = "http://localhost:8080/api/v1"
DEFAULT_GCP_URL = "https://technology-risk-register-bl7dub4c4a-uc.a.run.app/api/v1"

# Business Disruption Matrix for net exposure calculation
IMPACT_VALUES = {
    "Low": 1,
    "Moderate": 2,
    "Major": 3,
    "Catastrophic": 4
}

LIKELIHOOD_VALUES = {
    "Remote": 1,
    "Unlikely": 2,
    "Possible": 3,
    "Probable": 4
}

# Business Disruption Matrix (Impact × Likelihood → Score)
EXPOSURE_MATRIX = {
    (1, 1): 1,   # Low-Remote
    (1, 2): 2,   # Low-Unlikely
    (1, 3): 3,   # Low-Possible
    (1, 4): 5,   # Low-Probable
    (2, 1): 4,   # Moderate-Remote
    (2, 2): 6,   # Moderate-Unlikely
    (2, 3): 7,   # Moderate-Possible
    (2, 4): 9,   # Moderate-Probable
    (3, 1): 8,   # Major-Remote
    (3, 2): 10,  # Major-Unlikely
    (3, 3): 11,  # Major-Possible
    (3, 4): 13,  # Major-Probable
    (4, 1): 12,  # Catastrophic-Remote
    (4, 2): 14,  # Catastrophic-Unlikely
    (4, 3): 15,  # Catastrophic-Possible
    (4, 4): 16   # Catastrophic-Probable
}


class RiskLoadingError(Exception):
    """Custom exception for risk loading errors"""
    pass


class RiskLoader:
    """Risk loading client with configurable endpoints"""

    def __init__(self, api_url: str, dry_run: bool = False, verbose: bool = False, force_update: bool = False):
        self.api_url = api_url.rstrip('/')
        self.dry_run = dry_run
        self.verbose = verbose
        self.force_update = force_update

        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        # Setup HTTP session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.logger.info(f"Initialized RiskLoader for {api_url}")
        if dry_run:
            self.logger.info("DRY RUN MODE - No data will be posted to the API")

    def test_connection(self) -> bool:
        """Test connection to the API endpoint"""
        try:
            health_url = self.api_url.replace('/api/v1', '/health')
            response = self.session.get(health_url, timeout=10)
            response.raise_for_status()
            self.logger.info("✓ API connection successful")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"✗ API connection failed: {e}")
            return False

    def calculate_net_exposure(self, impact_rating: str, likelihood_rating: str) -> str:
        """Calculate business disruption net exposure"""
        impact_val = IMPACT_VALUES.get(impact_rating, 1)
        likelihood_val = LIKELIHOOD_VALUES.get(likelihood_rating, 1)

        exposure_number = EXPOSURE_MATRIX.get((impact_val, likelihood_val), 1)

        # Map to exposure categories
        if exposure_number <= 4:
            category = "Low"
        elif exposure_number <= 8:
            category = "Medium"
        elif exposure_number <= 12:
            category = "High"
        else:
            category = "Critical"

        return f"{category} ({exposure_number})"

    def parse_financial_amount(self, amount_str: str) -> Optional[float]:
        """Parse financial amounts from strings like '19,000,000'"""
        if not amount_str or amount_str.upper() == 'TBC':
            return None

        # Remove commas and convert to float
        cleaned = re.sub(r'[,\s]', '', str(amount_str))
        try:
            return float(cleaned)
        except ValueError:
            self.logger.warning(f"Could not parse financial amount: {amount_str}")
            return None

    def parse_date(self, date_str: str) -> str:
        """Parse date strings to ISO format"""
        try:
            # Handle format like "2025-08-28"
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            self.logger.warning(f"Could not parse date: {date_str}")
            return date_str

    def transform_risk_data(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform parsed risk data to API schema"""

        # Calculate net exposure
        impact_rating = risk_data.get('Business Disruption Impact Rating', 'Low')
        likelihood_rating = risk_data.get('Business Disruption Likelihood Rating', 'Remote')
        net_exposure = self.calculate_net_exposure(impact_rating, likelihood_rating)

        # Build API payload
        api_data = {
            "risk_id": risk_data.get('Risk ID'),
            "risk_title": risk_data.get('Risk Title'),
            "risk_category": risk_data.get('Risk Category'),
            "risk_description": risk_data.get('Risk Description', ''),
            "risk_status": risk_data.get('Risk Status', 'Active'),
            "risk_response_strategy": risk_data.get('Risk Response Strategy', 'Mitigate'),
            "planned_mitigations": risk_data.get('Planned Mitigations'),

            # Control fields - split coverage and effectiveness
            "preventative_controls_coverage": risk_data.get('Preventative Controls Coverage', 'No Controls'),
            "preventative_controls_effectiveness": risk_data.get('Preventative Controls Effectiveness', 'Not Possible to Assess'),
            "preventative_controls_description": risk_data.get('Preventative Controls Description'),
            "detective_controls_coverage": risk_data.get('Detective Controls Coverage', 'No Controls'),
            "detective_controls_effectiveness": risk_data.get('Detective Controls Effectiveness', 'Not Possible to Assess'),
            "detective_controls_description": risk_data.get('Detective Controls Description'),
            "corrective_controls_coverage": risk_data.get('Corrective Controls Coverage', 'No Controls'),
            "corrective_controls_effectiveness": risk_data.get('Corrective Controls Effectiveness', 'Not Possible to Assess'),
            "corrective_controls_description": risk_data.get('Corrective Controls Description'),

            # Ownership & Systems
            "risk_owner": risk_data.get('Risk Owner'),
            "risk_owner_department": risk_data.get('Risk Owner Department'),
            "systems_affected": risk_data.get('Systems Affected'),
            "technology_domain": risk_data.get('Technology Domain'),

            # Business Disruption Assessment
            "ibs_affected": risk_data.get('IBS Affected'),
            "business_disruption_impact_rating": impact_rating,
            "business_disruption_impact_description": risk_data.get('Business Disruption Impact Description', ''),
            "business_disruption_likelihood_rating": likelihood_rating,
            "business_disruption_likelihood_description": risk_data.get('Business Disruption Likelihood Description', ''),
            "business_disruption_net_exposure": net_exposure,

            # Financial Impact
            "financial_impact_low": self.parse_financial_amount(risk_data.get('Financial Impact (Low)')),
            "financial_impact_high": self.parse_financial_amount(risk_data.get('Financial Impact (High)')),
            "financial_impact_notes": risk_data.get('Financial Impact Notes'),

            # Dates
            "date_identified": self.parse_date(risk_data.get('Date Identified', '2025-01-01')),
            "last_reviewed": self.parse_date(risk_data.get('Last Reviewed', '2025-01-01')),
            "next_review_date": self.parse_date(risk_data.get('Next Review Date', '2025-01-01')),
        }

        # Remove None values
        return {k: v for k, v in api_data.items() if v is not None}

    def check_risk_exists(self, risk_id: str) -> bool:
        """Check if a risk already exists in the system"""
        try:
            get_url = urljoin(self.api_url + '/', f'risks/{risk_id}')
            response = self.session.get(get_url, timeout=30)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def update_risk(self, risk_id: str, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing risk via PUT"""
        try:
            # Transform data for API
            api_payload = self.transform_risk_data(risk_data)

            if self.verbose:
                self.logger.debug(f"UPDATE API payload for {risk_id}: {json.dumps(api_payload, indent=2)}")

            # PUT to API
            update_url = urljoin(self.api_url + '/', f'risks/{risk_id}')
            response = self.session.put(
                update_url,
                json=api_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            self.logger.info(f"✓ Successfully updated risk {risk_id}")
            return {"status": "success", "risk_id": risk_id, "result": result, "action": "updated"}

        except requests.exceptions.RequestException as e:
            error_msg = f"API update failed for {risk_id}: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {e.response.text[:200]}"

            self.logger.error(f"✗ {error_msg}")
            return {"status": "error", "risk_id": risk_id, "error": error_msg}

    def load_risk(self, risk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load a single risk via API with upsert logic"""
        risk_id = risk_data.get('Risk ID', 'Unknown')

        if self.dry_run:
            exists = self.check_risk_exists(risk_id)
            action = "update" if exists else "create"
            self.logger.info(f"[DRY RUN] Would {action} risk {risk_id}")
            return {"status": "dry_run", "risk_id": risk_id, "action": action}

        # Check if risk already exists
        exists = self.check_risk_exists(risk_id)

        if exists and not self.force_update:
            self.logger.info(f"⏭ Risk {risk_id} already exists (use --force-update to update)")
            return {"status": "skipped", "risk_id": risk_id, "reason": "already_exists"}
        elif exists and self.force_update:
            # Update existing risk
            return self.update_risk(risk_id, risk_data)
        else:
            # Create new risk
            try:
                # Transform data for API
                api_payload = self.transform_risk_data(risk_data)

                if self.verbose:
                    self.logger.debug(f"CREATE API payload for {risk_id}: {json.dumps(api_payload, indent=2)}")

                # Post to API
                create_url = urljoin(self.api_url + '/', 'risks/')
                response = self.session.post(
                    create_url,
                    json=api_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )

                response.raise_for_status()
                result = response.json()

                self.logger.info(f"✓ Successfully created risk {risk_id}")
                return {"status": "success", "risk_id": risk_id, "result": result, "action": "created"}

            except requests.exceptions.RequestException as e:
                # Check if it's a duplicate key error (risk was created between our check and create)
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 400:
                    try:
                        error_detail = e.response.json()
                        error_text = str(error_detail).lower()
                        if 'unique' in error_text or 'duplicate' in error_text or 'already exists' in error_text:
                            self.logger.info(f"⚠ Risk {risk_id} was created by another process, attempting update...")
                            return self.update_risk(risk_id, risk_data)
                    except:
                        pass

                error_msg = f"API request failed for {risk_id}: {e}"
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_detail = e.response.json()
                        error_msg += f" - {error_detail}"
                    except:
                        error_msg += f" - {e.response.text[:200]}"

                self.logger.error(f"✗ {error_msg}")
                return {"status": "error", "risk_id": risk_id, "error": error_msg}


def get_risk_data() -> List[Dict[str, Any]]:
    """Get the 11 technology risks data"""
    return [
        {
            "Risk ID": "TR-2025-001",
            "Risk Title": "Enterprise Data Loss Event",
            "Risk Category": "Data Management",
            "Risk Description": "Local (aka native) backups with or without defined RPO/RTO targets can fail due to critical risk events such as misconfiguration (UniSuper-style account deletion), backup system failures (OVH fire), and ransomware attacks (Kaseya-style encryption). No enterprise-wide 3-2-1 backup strategy exists with applications relying solely on cloud-provider native backup solutions. In most cases, undefined RTO/RPO targets and untested recovery procedures create potential for permanent data loss and business closure.",
            "Risk Status": "Active",
            "Risk Owner": "Tom Yandell",
            "Risk Owner Department": "Information Technology",
            "Technology Domain": "Data/Databases",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "All systems with permanent data storage or configuration repositories",
            "IBS Affected": "ALL",
            "Business Disruption Impact Rating": "Catastrophic",
            "Business Disruption Impact Description": "IBS will be severely disrupted without a recoverable backup and process to restore. The outages could be weeks/months and reputational damage impaired and likely in some cases, completely fail. A full simulated series of non-functional tests in a fully loaded near identical non-production environment is required for each of the IBS applications to determine the full outcome native backup failure event.",
            "Business Disruption Likelihood Rating": "Possible",
            "Business Disruption Likelihood Description": "Control gaps across all pillars but specifically with the most critical safeguards such as preventative backup testing and integrity monitoring, the detective SOC and TOC and finally the corrective 3-2-1 backups. The Sentinel project maturation of BCP is essential and this scenario must be considered critical in their planning.",
            "Preventative Controls Coverage": "Incomplete Coverage",
            "Preventative Controls Effectiveness": "Partially Effective",
            "Preventative Controls Description": "**Configuration Drift Detection** - CSPM tool, Wiz, in place, Azure Config in place. Overall infra state drift tool missing. **Backup Testing and Integrity Monitoring** - no regular testing in place, and no integrity tool(s) are being used. **Endpoint Detection and Response** - DarkTrace and Microsoft Defender are being reviewed although not clear whether server EP are covered.",
            "Detective Controls Coverage": "Incomplete Coverage",
            "Detective Controls Effectiveness": "Not Possible to Assess",
            "Detective Controls Description": "**Security and Technology Operation Centres** - SOC service integration with Ontinue progressing for October 2025; build-it-run-it TOC model under development.",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Not Possible to Assess",
            "Corrective Controls Description": "**Business Continuity Site Activation** - BCP plan in development through project Sentinel. **3-2-1 Backup Strategy** - No strategy in place, dependent on native backup. **Crisis Communication and Stakeholder Management** - BCP plan in development through project Sentinel. **Emergency Vendor and Service Provider Activation** - BCP plan in development through project Sentinel.",
            "Financial Impact (Low)": "19000000",
            "Financial Impact (High)": "250000000",
            "Financial Impact Notes": "**Low:** 1 week outage / 100% of GWP **High:** 3 months outage / 100% of GWP",
            "Planned Mitigations": "TBC",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-10-08"
        },
        {
            "Risk ID": "TR-2025-002",
            "Risk Title": "GKE Platform Multi-Tenant Failure",
            "Risk Category": "Infrastructure",
            "Risk Description": "Multi-tenant GKE platform hosting all front-office systems suffers from infrastructure challenges including resource management guardrails such as memory exhaustion incidents from misconfigured applications, single load balancer dependency for customer whitelisting, and inability to test non-functional failure scenarios due to lack of environment(s). Platform failure would simultaneously affect all containerised workloads preventing quote generation, data analytics, and customer services.",
            "Risk Status": "Active",
            "Risk Owner": "Tom Yandell",
            "Risk Owner Department": "Information Technology",
            "Technology Domain": "Infrastructure",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "Algo, DSS, KiWeb, all GKE-hosted front-office applications",
            "IBS Affected": "ALL front-office IBS",
            "Business Disruption Impact Rating": "Moderate",
            "Business Disruption Impact Description": "IBS will be impaired and could in some cases completely fail. All front-office applications (Algo, DSS, KiWeb) simultaneously affected during platform failures. Quote generation and customer service response times severely impacted. A full simulated series of non-functional tests in a fully loaded near identical non-production environment is required for each of the IBS applications to determine the full outcome of a GKE disruption event.",
            "Business Disruption Likelihood Rating": "Possible",
            "Business Disruption Likelihood Description": "Control gaps in preventative measures and incomplete implementation of corrective and detective controls. While cluster capacity is adequate, workload-level configurations for resource management and zone distribution are not enforced, and testing capabilities remain limited.",
            "Preventative Controls Coverage": "No Controls",
            "Preventative Controls Effectiveness": "Not Possible to Assess",
            "Preventative Controls Description": "**Chaos Engineering** - No capability implemented; single production environment prevents failure testing. **Disconnected Testing** - Not possible as capability not implemented in any environment. **Resource management -** Improvements underway but preventative testing remains difficult without adequate test environment.",
            "Detective Controls Coverage": "Incomplete Coverage",
            "Detective Controls Effectiveness": "Partially Effective",
            "Detective Controls Description": "**Observability** - Grafana and Prometheus federated to Google Managed Prometheus providing external visibility. However, missing alerts for cross-platform dependencies and some monitoring gaps remain. Google Cloud Monitoring provides cluster health monitoring but would struggle with significant lights-out service incidents.",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Partially Effective",
            "Corrective Controls Description": "**Multi-Zone Rescheduling** - Multi-zone GKE implemented with adequate resource capacity for zone failures. However, workloads lack anti-affinity configurations. **Reduced Blast Radius** - Spitting out critical application, not implemented. **Adequate Resources** - Partially implemented with doubled capacity but workload resource requests/limits not properly configured. **3rd Line Support** - Run-books and rehearsals possible and partially implemented.",
            "Financial Impact (Low)": "1500000",
            "Financial Impact (High)": "4000000",
            "Financial Impact Notes": "**Low:** 3 hours outage / 100% of GWP **High:** 1 day outage / 100% of GWP",
            "Planned Mitigations": "Migration to 10.x network, dedicated node pools for critical workloads, comprehensive testing environment, chaos engineering implementation",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-10-08"
        },
        {
            "Risk ID": "TR-2025-003",
            "Risk Title": "Identity Provider Cascade Failure",
            "Risk Category": "Cybersecurity",
            "Risk Description": "Ki operates dual-tenant identity architecture with both Azure and GCP foundations depending entirely on Brit-managed Entra ID without an off-site data back-up or secondary authentication systems. Identity provider failure would immediately disable access to M365, cloud foundations, and federated SaaS applications, with cascade effects lasting 90 minutes to 14 hours based on historical Microsoft Entra incidents (2021, 2024, 2025).",
            "Risk Status": "Active",
            "Risk Owner": "Sean Duff",
            "Risk Owner Department": "Infrastructure",
            "Technology Domain": "Security Systems",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "M365 suite, Azure/GCP portals, all federated SaaS applications, Infrastructure-as-Code via GitHub",
            "IBS Affected": "TBC",
            "Business Disruption Impact Rating": "Moderate",
            "Business Disruption Impact Description": "Ki business and technology operational staff will be shut out of most tools and services. Front office access is token based thus customers should not be immediately impacted. Although back office applications are mostly SaaS or Azure hosted and will be impacted. Complete authentication failure with existing tokens expiring causing cascading service failures.",
            "Business Disruption Likelihood Rating": "Probable",
            "Business Disruption Likelihood Description": "Control gaps in preventative measures and incomplete implementation of corrective and detective controls, with most critical safeguards like secondary IdP, break glass procedures, and synthetic testing either not implemented or not fully deployed. Likely to occur more frequently than every 5 years based on past incidents.",
            "Preventative Controls Coverage": "No Controls",
            "Preventative Controls Effectiveness": "Not Possible to Assess",
            "Preventative Controls Description": "**Change Management** - Not possible as customers cannot control Microsoft deployment processes. **Vendor Management** - Not implemented; no monthly business reviews with Microsoft. **Canary Deployments** - Not possible with Entra in current architecture.",
            "Detective Controls Coverage": "Incomplete Coverage",
            "Detective Controls Effectiveness": "Not Possible to Assess",
            "Detective Controls Description": "**Synthetic Testing** - Not implemented; no periodic authentication testing across IBS or Azure Service Health API integration for proactive incident detection.",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Not Possible to Assess",
            "Corrective Controls Description": "**Secondary IdP** - Okta configured as identity broker only, not standalone IdP. **DR and Backup** - Not implemented; Rubrik planned but not deployed. **Break Glass** - Partially implemented with 1Password for platform teams, documented Azure/M365 run book exists. **3rd Line Support** - Partially implemented with MS Graph API access and GitHub maintaining Azure resource access.",
            "Financial Impact (Low)": "500000",
            "Financial Impact (High)": "2000000",
            "Financial Impact Notes": "**Low:** 4 hours outage / 25% of GWP **High:** 2 days outage / 25% of GWP",
            "Planned Mitigations": "Convert Okta from broker/bridge to secondary IdP, implement comprehensive break-glass procedures, deploy synthetic authentication monitoring.",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-10-08"
        },
        {
            "Risk ID": "TR-2025-004",
            "Risk Title": "Cross-Cloud Connectivity Failure",
            "Risk Category": "Infrastructure",
            "Risk Description": "Internet-based network connectivity without redundant paths between Azure and GCP, and to critical external services including SaaS applications requiring federated authentication. Network failures would disrupt cross-cloud data flows, external system integration, and critical business processes dependent on multi-cloud architecture.",
            "Risk Status": "Active",
            "Risk Owner": "Sean Duff",
            "Risk Owner Department": "Information Technology",
            "Technology Domain": "Network/Communications",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "Cross-cloud data flows, external SaaS integrations, critical SaaS applications requiring federated authentication",
            "IBS Affected": "TBC",
            "Business Disruption Impact Rating": "Moderate",
            "Business Disruption Impact Description": "Cross-cloud integration failures, loss to critical SaaS and PaaS and CSP hosted services causing disruption. Degraded performance for integrated services with data synchronisation delays and external API timeouts affecting business processes.",
            "Business Disruption Likelihood Rating": "Possible",
            "Business Disruption Likelihood Description": "Partial preventative controls in place with redundant internet-based VPN connections designed and some network monitoring. Adequate detective controls with network monitoring and alerting. Limited redundancy in corrective controls with manual failover procedures.",
            "Preventative Controls Coverage": "Incomplete Coverage",
            "Preventative Controls Effectiveness": "Partially Effective",
            "Preventative Controls Description": "**Network Architecture** - Redundant internet-based VPN connections between clouds without private connectivity. Some network monitoring in place but lacks redundant paths to critical external services. **Private Links** - use of dedicated private links e.g. GCP Direct Connect, Azure Express Route, Z-Scaler etc, between CSPs and critical services.",
            "Detective Controls Coverage": "Incomplete Coverage",
            "Detective Controls Effectiveness": "Partially Effective",
            "Detective Controls Description": "**Network Monitoring** - Network monitoring and alerting systems in place on the Azure side of the VPN connectivity, the GCP side TBC. Connectivity to critical third parties are not being monitored. Single agnostic observability tool should be used across all critical network connectivity e.g. DataDog, ThousandEyes etc",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Partially Effective",
            "Corrective Controls Description": "**Automatic Failover** - Automatic route failover can be used for HL VPN on the Azure side, not clear how the implementation world on the GCP side. Currently all outbound network to critical third party services is via internet gateways.",
            "Financial Impact (Low)": "1000000",
            "Financial Impact (High)": "2000000",
            "Financial Impact Notes": "**Low:** 4 hours outage / 50% of GWP **High:** 1 day outage / 50% of GWP",
            "Planned Mitigations": "Private connectivity implementation, redundant network paths, address network SME skill gaps",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-12-08"
        },
        {
            "Risk ID": "TR-2025-005",
            "Risk Title": "Observability Vendor Lights Out Risk",
            "Risk Category": "Operational",
            "Risk Description": "Cloud-vendor specific monitoring tools creating potential observability blind spots during significant provider outages. Limited ability to correlate incidents across multi-cloud environment affecting incident response. Azure uses native monitoring tools, GCP relies on Google-native solutions, creating fragmented visibility during cross-platform troubleshooting.",
            "Risk Status": "Active",
            "Risk Owner": "Sean Duff",
            "Risk Owner Department": "Information Technology",
            "Technology Domain": "Infrastructure",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "All multi-cloud applications and infrastructure",
            "IBS Affected": "TBC",
            "Business Disruption Impact Rating": "Moderate",
            "Business Disruption Impact Description": "Extended incident resolution times during multi-cloud issues. Limited to no visibility during significant CSP incidences affects ability to maintain service levels. Delayed detection of service degradation impacts customer experience.",
            "Business Disruption Likelihood Rating": "Possible",
            "Business Disruption Likelihood Description": "Partial controls in place with separate monitoring tools for each CSP platform. Cross-platform correlation limited to manual processes. Cloud-agnostic observability platform needed for comprehensive visibility across all infrastructure platforms and applications.",
            "Preventative Controls Coverage": "No Controls",
            "Preventative Controls Effectiveness": "Not Possible to Assess",
            "Preventative Controls Description": "**Platform-Agnostic Monitoring** - No single platform agnostic observability tool in use. No cross-platform correlation capabilities. **Centralised Logging** - Although a SEIM is in place for system logs, application logs are not being centralised. Most observability agnostic tools support this ability",
            "Detective Controls Coverage": "No Controls",
            "Detective Controls Effectiveness": "Not Possible to Assess",
            "Detective Controls Description": "**Platform-Agnostic Monitoring** - No single platform agnostic observability tool in use. No cross-platform correlation capabilities. **Centralised Logging** - Although a SEIM is in place for system logs, application logs are not being centralised. Most observability agnostic tools support this ability",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Partially Effective",
            "Corrective Controls Description": "**Platform-Agnostic Monitoring** - No single platform agnostic observability tool in use. No cross-platform correlation capabilities. **3rd Line Support** - Separate incident response procedures for each platform. Manual correlation required during cross-platform issues affecting response time and effectiveness.",
            "Financial Impact (Low)": "1000000",
            "Financial Impact (High)": "4000000",
            "Financial Impact Notes": "**Low:** 4 hours outage / 50% of GWP **High:** 1 days outage / 50% of GWP",
            "Planned Mitigations": "Cloud-agnostic observability platform, centralised log aggregation, Azure Service Health API integration",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-12-08"
        },
        {
            "Risk ID": "TR-2025-006",
            "Risk Title": "Azure IaaS High Availability Gaps",
            "Risk Category": "Application",
            "Risk Description": "Critical IaaS applications (Tyche and Phinsys) exhibit significant single points of failure including single IaaS SQL Server instances, single-zone deployments, and manual recovery processes. Phinsys supports critical quarter-end reporting operations and Tyche is classified as a tier-one business application with aggressive RTO/RPO targets (15 minutes/4 hours) but no formal testing validation.",
            "Risk Status": "Active",
            "Risk Owner": "Ian Hurst",
            "Risk Owner Department": "Information Technology",
            "Technology Domain": "Applications",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "Tyche (tier-one application), Phinsys (quarter-end reporting platform)",
            "IBS Affected": "2",
            "Business Disruption Impact Rating": "Major",
            "Business Disruption Impact Description": "Quarter-end reporting capabilities at risk affecting regulatory compliance. Tyche business requirements disconnect with tier-one classification but inadequate resilience architecture. Extended recovery times during failures with manual processes only.",
            "Business Disruption Likelihood Rating": "Possible",
            "Business Disruption Likelihood Description": "Single points of failure throughout architecture with predominantly manual processes. No formal SLAs or business requirements documentation. Ad-hoc operations with limited operational procedures and no continuous improvement processes.",
            "Preventative Controls Coverage": "Incomplete Coverage",
            "Preventative Controls Effectiveness": "Not Possible to Assess",
            "Preventative Controls Description": "**HA Architecture** - Basic VM deployment with limited redundancy. Hardware-bound licensing creating constraints for automated recovery. No highly available multi-zone deployment implemented. **PaaS Services** - No use of HA PaaS service such as Managed SQL Server or Application Server",
            "Detective Controls Coverage": "Incomplete Coverage",
            "Detective Controls Effectiveness": "Partially Effective",
            "Detective Controls Description": "**Monitoring and Alerting** - Basic monitoring and alerting capabilities. No comprehensive application health monitoring or proactive failure detection.",
            "Corrective Controls Coverage": "No Controls",
            "Corrective Controls Effectiveness": "Not Possible to Assess",
            "Corrective Controls Description": "**Automated Redundancy** - No automated failover capabilities. Manual recovery processes only without tested procedures. No active-passive database configuration or zone redundancy. No active-active application servers. **3rd Line Support** - Operation team is forming although it is not clear whether the build-it / run-it model will be used for these applications.",
            "Financial Impact (Low)": "TBC",
            "Financial Impact (High)": "TBC",
            "Financial Impact Notes": "**Low:** TBC **High:** TBC",
            "Planned Mitigations": "Multi-zone HA deployment, migration to managed database services, automated scaling, operational excellence framework",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-10-08"
        },
        {
            "Risk ID": "TR-2025-007",
            "Risk Title": "Disaster Recovery Testing Gaps",
            "Risk Category": "Regulatory/Compliance",
            "Risk Description": "Systematic absence of disaster recovery testing across all applications with undefined RTO/RPO targets and untested recovery procedures. This creates regulatory compliance exposure and unknown recovery capabilities during actual incidents. No formal DR testing schedule exists with some applications relying on manual recovery procedures that have never been validated.",
            "Risk Status": "Active",
            "Risk Owner": "Richard Bradley",
            "Risk Owner Department": "Legal/Compliance",
            "Technology Domain": "Applications",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "All critical applications and data systems",
            "IBS Affected": "ALL",
            "Business Disruption Impact Rating": "Major",
            "Business Disruption Impact Description": "Unknown recovery capabilities threaten all SLA commitments. Inability to validate recovery time objectives creates regulatory compliance risk. Extended outages possible during actual disasters due to untested procedures.",
            "Business Disruption Likelihood Rating": "Probable",
            "Business Disruption Likelihood Description": "No systematic DR testing procedures exist. Most applications have undefined RTO/RPO targets. Recovery procedures exist but remain untested across the enterprise creating high likelihood of failure during actual incidents.",
            "Preventative Controls Coverage": "No Controls",
            "Preventative Controls Effectiveness": "Not Possible to Assess",
            "Preventative Controls Description": "**DR Testing Framework** - No systematic DR testing procedures implemented. No formal testing schedule or chaos engineering practices to validate recovery capabilities. **DR Testing Schedule** - No formal testing schedule and execution to validate recovery capabilities. **Chaos Engineering** - No chaos engineering practices in place",
            "Detective Controls Coverage": "No Controls",
            "Detective Controls Effectiveness": "Not Possible to Assess",
            "Detective Controls Description": "**DR Test Validation** - No validation of recovery capabilities or monitoring of DR readiness. No testing results analysis or gap identification processes.",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Partially Effective",
            "Corrective Controls Description": "**DR Plan Execution** - Some manual recovery procedures exist although no failover and fail back tests have been carried out. **Automatic Failover / Fail back** - No automated failover capabilities or validated recovery processes across critical applications.",
            "Financial Impact (Low)": "2000000",
            "Financial Impact (High)": "6000000",
            "Financial Impact Notes": "**Low:** 1 day outage / 50% of GWP **High:** 3 days outage / 50% of GWP",
            "Planned Mitigations": "Formal DR testing procedures, chaos engineering implementation, regular testing schedule, RTO/RPO definition",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-10-08"
        },
        {
            "Risk ID": "TR-2025-008",
            "Risk Title": "Critical Third-Party Service",
            "Risk Category": "Vendor/Third Party",
            "Risk Description": "Dependencies on external services including managed General Ledger, Eclipse systems, and other third-party providers without comprehensive availability monitoring or alternative solutions. Limited Third Party Risk Management (TPRM) reviews for business-critical managed services. Failures could disrupt critical business operations with dependency on third-party provider SLAs.",
            "Risk Status": "Active",
            "Risk Owner": "Po-Wah Yau",
            "Risk Owner Department": "Business Units",
            "Technology Domain": "Cloud Services",
            "Risk Response Strategy": "Transfer",
            "Systems Affected": "General Ledger, Eclipse, other managed services",
            "IBS Affected": "TBC",
            "Business Disruption Impact Rating": "Moderate",
            "Business Disruption Impact Description": "Service degradation during provider outages affecting dependent business processes. Reliance on third-party provider SLAs for service restoration. Limited workarounds available during extended outages.",
            "Business Disruption Likelihood Rating": "Possible",
            "Business Disruption Likelihood Description": "Partial controls in place through service agreements and SLAs with providers. Limited monitoring of third-party service availability. Escalation procedures exist but alternative providers not evaluated.",
            "Preventative Controls Coverage": "Incomplete Coverage",
            "Preventative Controls Effectiveness": "Partially Effective",
            "Preventative Controls Description": "**Service Agreements** - SLAs and service agreements in place with critical providers. However, limited TPRM reviews and no alternative service provider evaluations conducted. **QIA / Qualifying NFRs** - Not in place at the time of vendor selection or on-boarding. Grandfathering in these processes with business owners.",
            "Detective Controls Coverage": "No Controls",
            "Detective Controls Effectiveness": "Not Possible to Assess",
            "Detective Controls Description": "**Agnostic Observability**  - No monitoring of third-party service availability. Reliance on provider status pages and notifications. Some agnostic observability and posture management tools can monitor and alert.",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Partially Effective",
            "Corrective Controls Description": "**Vendor Escalation** - Escalation procedures with vendors exist. However, no alternative providers identified and business continuity plans for extended outages not developed. **Exit Strategy** - no comprehensive exit process with incident triage, escalation and trigger events in place",
            "Financial Impact (Low)": "2000000",
            "Financial Impact (High)": "25000000",
            "Financial Impact Notes": "**Low:** 1 week poor service / 10% of GWP **High:** 3 months poor service / 10% of GWP",
            "Planned Mitigations": "Vendor risk assessments, alternative provider evaluation, enhanced monitoring, TPRM framework implementation",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-12-08"
        },
        {
            "Risk ID": "TR-2025-009",
            "Risk Title": "Regional Disaster Recovery Limitations",
            "Risk Category": "Infrastructure",
            "Risk Description": "GCP and Azure foundations operate in single region (by design) with no multi-region disaster recovery capabilities. Regional disasters could cause extended outages with unknown recovery times. Single region limitation creates regional data disaster recovery gap requiring Ki-wide data recovery standards.",
            "Risk Status": "Active",
            "Risk Owner": "Thomas Yandell",
            "Risk Owner Department": "Information Technology",
            "Technology Domain": "Infrastructure",
            "Risk Response Strategy": "Accept",
            "Systems Affected": "All Azure-hosted applications, some GCP applications",
            "IBS Affected": "Region-dependent IBS",
            "Business Disruption Impact Rating": "Catastrophic",
            "Business Disruption Impact Description": "Extended regional outages would breach all SLAs. Recovery dependent on regional disaster scope. Azure applications particularly vulnerable due to single AZ deployment with manual failover procedures. Multi-zone deployment provides some resilience but insufficient for regional disasters.",
            "Business Disruption Likelihood Rating": "Remote",
            "Business Disruption Likelihood Description": "Regional disasters are rare but catastrophic when they occur. Multi-zone deployment within regions provides very good resilience. However applications not designed to be multi-AZ will remain at high risk.",
            "Preventative Controls Coverage": "Incomplete Coverage",
            "Preventative Controls Effectiveness": "Partially Effective",
            "Preventative Controls Description": "**Multi-Zone Deployments** - Applications designed with multi-zone deployment implemented within regions providing resilience against availability zone failures but not regional disasters. **Multi-Region Deployments** - This is not a Ki standard or with-in appetite",
            "Detective Controls Coverage": "Incomplete Coverage",
            "Detective Controls Effectiveness": "Not Possible to Assess",
            "Detective Controls Description": "**Regional Service Health Monitoring** - Each CSP does have regional health monitoring that provides  visibility into service level regional status, although it is not an agnostic observability option. It is not clear whether any alerts are in place.",
            "Corrective Controls Coverage": "No Controls",
            "Corrective Controls Effectiveness": "Not Possible to Assess",
            "Corrective Controls Description": "**Region Failover** - No cross-region failover capabilities implemented or planned.",
            "Financial Impact (Low)": "4000000",
            "Financial Impact (High)": "12000000",
            "Financial Impact Notes": "**Low:** 1 day outage / 100% of GWP **High:** 3 days outage / 100% of GWP",
            "Planned Mitigations": "No mitigation planned",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-12-08"
        },
        {
            "Risk ID": "TR-2025-010",
            "Risk Title": "Application-Specific Resilience Gaps",
            "Risk Category": "Application",
            "Risk Description": "Critical and high priority resilience improvements identified in individual application assessments remain unimplemented across the application portfolio. These include Algo's disaster recovery and resilience testing gaps, DSS's observability and SLO definition requirements, KiWeb's ownership resolution and fault tolerance improvements, and GKE platform's reliability targets and testing environments. Failure to implement these application-specific actions leaves individual applications vulnerable despite enterprise-level improvements.",
            "Risk Status": "Active",
            "Risk Owner": "Chris Tunecliff, Richard Hogarth",
            "Risk Owner Department": "Information Technology",
            "Technology Domain": "Applications",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "Algo, DSS, KiWeb, Tyche, Phinsys, GKE Foundation, Azure Foundation",
            "IBS Affected": "6",
            "Business Disruption Impact Rating": "Major",
            "Business Disruption Impact Description": "Individual application failures despite enterprise resilience improvements. Algo lacks formal disaster recovery capabilities and resilience validation. DSS missing comprehensive observability and SLO monitoring. KiWeb ownership tension preventing investment prioritization. GKE platform reliability targets undefined affecting all containerized workloads. Application-specific gaps create service degradation and extended recovery times.",
            "Business Disruption Likelihood Rating": "Probable",
            "Business Disruption Likelihood Description": "Application assessment identified specific critical and high priority gaps that require prioritisation and resourcing to complete. Without focused application-level improvements, enterprise resilience initiatives alone insufficient to achieve target reliability levels. Resource constraints and competing priorities likely to delay implementation.",
            "Preventative Controls Coverage": "Incomplete Coverage",
            "Preventative Controls Effectiveness": "Partially Effective",
            "Preventative Controls Description": "**Application Architecture** - Some applications have good technical architecture (Algo redundancy, DSS infrastructure foundations) but lack application-specific resilience patterns. **Chaos Engineering** - Limited to individual-driven chaos engineering without organisational process. No systematic application resilience validation. **SLA/SLO/RTO/RPO** - not properly defined resiliency metrics that are adhered to by most applications",
            "Detective Controls Coverage": "Incomplete Coverage",
            "Detective Controls Effectiveness": "Partially Effective",
            "Detective Controls Description": "**Health Checks** - Varies by application with some having good observability foundations but missing proactive failure detection.",
            "Corrective Controls Coverage": "Incomplete Coverage",
            "Corrective Controls Effectiveness": "Partially Effective",
            "Corrective Controls Description": "**Recovery Procedures** - Application-specific disaster recovery procedures undefined or untested. **Fault Tolerance** - Limited circuit breaker patterns and graceful degradation capabilities. **Operational Procedures** - Application run books and incident response procedures need standardisation and testing.",
            "Financial Impact (Low)": "1000000",
            "Financial Impact (High)": "2000000",
            "Financial Impact Notes": "**Low:** 4 hours outage / 50% of GWP **High:** 1 day outage / 50% of GWP",
            "Planned Mitigations": "Algo: DR testing, resilience validation, fault tolerance patterns. DSS: Observability implementation, SLO definition, DR procedures. KiWeb: Ownership resolution, fault tolerance, DR implementation. GKE: Reliability targets, testing environments, resource governance. Application-specific operational excellence. Tyche and Phinsys: need to complete migration with signed off DR execution etc",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-10-08"
        },
        {
            "Risk ID": "TR-2025-011",
            "Risk Title": "Business Continuity Plan Maturity Gaps",
            "Risk Category": "Operational",
            "Risk Description": "Business Continuity Plan (BCP) is under development through Project Sentinel with critical gaps in crisis communication protocols, emergency vendor activation procedures, alternative site planning, DR execution plan, and stakeholder management frameworks. BCP immaturity limits organisational response capability during major incidents across all failure scenarios. Technical vendor escalation managed separately from operational BCP creating coordination challenges.",
            "Risk Status": "Active",
            "Risk Owner": "Richard Bradley",
            "Risk Owner Department": "Operations",
            "Technology Domain": "Applications",
            "Risk Response Strategy": "Mitigate",
            "Systems Affected": "All critical business operations during major incidents",
            "IBS Affected": "ALL",
            "Business Disruption Impact Rating": "Major",
            "Business Disruption Impact Description": "Extended recovery times due to lack of coordinated response procedures. Uncoordinated incident response affecting all service recovery objectives. Poor stakeholder communication during crises affecting customer and regulatory confidence.",
            "Business Disruption Likelihood Rating": "Possible",
            "Business Disruption Likelihood Description": "BCP framework under development but not yet implemented. No established crisis communication protocols or DR execution plans. Emergency vendor procedures undefined creating high likelihood of coordination failures during major incidents.",
            "Preventative Controls Coverage": "No Controls",
            "Preventative Controls Effectiveness": "Not Possible to Assess",
            "Preventative Controls Description": "**BCP Framework** - No established BCP framework or alternative operational sites. Project Sentinel in development phase but preventative controls not yet implemented.",
            "Detective Controls Coverage": "No Controls",
            "Detective Controls Effectiveness": "Not Possible to Assess",
            "Detective Controls Description": "**BCP Execution Plan** - No BCP testing or validation procedures implemented. No capability to assess BCP readiness or effectiveness.",
            "Corrective Controls Coverage": "No Controls",
            "Corrective Controls Effectiveness": "Not Possible to Assess",
            "Corrective Controls Description": "**BCP** - Project Sentinel BCP in development. Crisis communication protocols undefined. Emergency vendor activation procedures not established. DR execution plan and technical and operational BCP coordination not defined.",
            "Financial Impact (Low)": "4000000",
            "Financial Impact (High)": "12000000",
            "Financial Impact Notes": "**Low:** 1 day outage / 100% of GWP **High:** 3 days outage / 100% of GWP",
            "Planned Mitigations": "Complete Project Sentinel BCP development, establish crisis communication frameworks, pre-contract emergency vendors, integrate technical and operational response procedures",
            "Date Identified": "2025-08-28",
            "Last Reviewed": "2025-09-08",
            "Next Review Date": "2025-10-08"
        }
    ]


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Load technology risks into Risk Register system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --local                              # Load to localhost:8080
  %(prog)s --prod                               # Load to GCP endpoint
  %(prog)s --api-url https://custom.com/api/v1  # Load to custom endpoint
  %(prog)s --prod --dry-run                     # Validate without posting
  %(prog)s --local --risk-ids TR-2025-001       # Load specific risk
  %(prog)s --prod --force-update                # Always update existing risks
        """
    )

    # Environment selection (mutually exclusive)
    env_group = parser.add_mutually_exclusive_group()
    env_group.add_argument('--local', action='store_true',
                          help='Load to local development environment (localhost:8008)')
    env_group.add_argument('--prod', action='store_true',
                          help='Load to GCP production environment')
    env_group.add_argument('--api-url', type=str,
                          help='Custom API base URL (e.g., https://api.example.com/api/v1)')

    # Options
    parser.add_argument('--dry-run', action='store_true',
                       help='Validate data without posting to API')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--risk-ids', type=str,
                       help='Comma-separated list of specific risk IDs to load')
    parser.add_argument('--force-update', action='store_true',
                       help='Always update existing risks instead of skipping them')

    args = parser.parse_args()

    # Determine API URL
    if args.local:
        api_url = DEFAULT_LOCAL_URL
    elif args.prod:
        api_url = DEFAULT_GCP_URL
    elif args.api_url:
        api_url = args.api_url
    else:
        # Default to local
        api_url = DEFAULT_LOCAL_URL
        print("No environment specified, defaulting to --local")

    print(f"Risk Register Loading Tool")
    print(f"Target: {api_url}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("-" * 50)

    # Initialize loader
    loader = RiskLoader(api_url, dry_run=args.dry_run, verbose=args.verbose, force_update=args.force_update)

    # Test connection
    if not loader.test_connection():
        print("Failed to connect to API. Please check the endpoint and try again.")
        sys.exit(1)

    # Get risk data
    risks = get_risk_data()

    if not risks:
        print("No risk data found. Please check the risk data source.")
        sys.exit(1)

    # Filter risks if specific IDs requested
    if args.risk_ids:
        requested_ids = [rid.strip() for rid in args.risk_ids.split(',')]
        risks = [r for r in risks if r.get('Risk ID') in requested_ids]
        print(f"Loading {len(risks)} specific risks: {requested_ids}")
    else:
        print(f"Loading {len(risks)} risks")

    # Load risks
    results = []
    for i, risk in enumerate(risks, 1):
        risk_id = risk.get('Risk ID', f'Risk-{i}')
        print(f"[{i}/{len(risks)}] Processing {risk_id}...")

        result = loader.load_risk(risk)
        results.append(result)

    # Summary
    print("\n" + "=" * 50)
    print("LOADING SUMMARY")
    print("=" * 50)

    successful = len([r for r in results if r['status'] == 'success'])
    errors = len([r for r in results if r['status'] == 'error'])
    dry_runs = len([r for r in results if r['status'] == 'dry_run'])
    skipped = len([r for r in results if r['status'] == 'skipped'])

    print(f"Total processed: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Errors: {errors}")
    if skipped > 0:
        print(f"Skipped: {skipped}")
    if dry_runs > 0:
        print(f"Dry runs: {dry_runs}")

    # Show actions breakdown for successful operations
    if successful > 0:
        created = len([r for r in results if r['status'] == 'success' and r.get('action') == 'created'])
        updated = len([r for r in results if r['status'] == 'success' and r.get('action') == 'updated'])
        if created > 0:
            print(f"  - Created: {created}")
        if updated > 0:
            print(f"  - Updated: {updated}")

    # Show errors
    error_results = [r for r in results if r['status'] == 'error']
    if error_results:
        print(f"\nErrors:")
        for result in error_results:
            print(f"  - {result['risk_id']}: {result['error']}")

    print(f"\nCompleted!")

    # Exit with error code if there were failures
    sys.exit(1 if errors > 0 else 0)


if __name__ == '__main__':
    main()
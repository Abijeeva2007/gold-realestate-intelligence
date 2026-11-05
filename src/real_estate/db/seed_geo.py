"""
Statewide Geographic Master & Seed Script for Tamil Nadu Real Estate Intelligence Engine.
Populates all 38 districts of Tamil Nadu, key taluks, prominent localities,
property types, registered data sources, and strategic infrastructure corridors.
"""

from datetime import datetime, date
from sqlalchemy.orm import Session
from src.real_estate.db.database import get_real_estate_engine, SessionLocal, Base
from src.real_estate.db.schema import (
    District, Taluk, Locality, PropertyType, DataSource,
    InfrastructureProject, MarketIndex, MacroIndicator
)
from src.real_estate.config import REAL_ESTATE_SOURCES, PROPERTY_CATEGORIES


# Complete 38 Districts of Tamil Nadu
TAMIL_NADU_DISTRICTS = [
    {"code": "CHN", "name": "Chennai", "headquarters": "Chennai", "region": "Northern", "lat": 13.0827, "lon": 80.2707, "area": 426.0, "pop": 7088403},
    {"code": "CGL", "name": "Chengalpattu", "headquarters": "Chengalpattu", "region": "Northern", "lat": 12.6841, "lon": 79.9836, "area": 2945.0, "pop": 2556244},
    {"code": "TLR", "name": "Tiruvallur", "headquarters": "Tiruvallur", "region": "Northern", "lat": 13.1432, "lon": 79.9079, "area": 3422.0, "pop": 3728104},
    {"code": "KCH", "name": "Kanchipuram", "headquarters": "Kanchipuram", "region": "Northern", "lat": 12.8342, "lon": 79.7036, "area": 1704.0, "pop": 1166401},
    {"code": "VEL", "name": "Vellore", "headquarters": "Vellore", "region": "Northern", "lat": 12.9165, "lon": 79.1325, "area": 2038.0, "pop": 1614242},
    {"code": "RPT", "name": "Ranipet", "headquarters": "Ranipet", "region": "Northern", "lat": 12.9298, "lon": 79.3327, "area": 2234.0, "pop": 1210277},
    {"code": "TPT", "name": "Tirupathur", "headquarters": "Tirupathur", "region": "Northern", "lat": 12.4965, "lon": 78.5678, "area": 1797.0, "pop": 1111812},
    {"code": "TVM", "name": "Tiruvannamalai", "headquarters": "Tiruvannamalai", "region": "Northern", "lat": 12.2253, "lon": 79.0747, "area": 6191.0, "pop": 2464875},
    {"code": "VPM", "name": "Viluppuram", "headquarters": "Viluppuram", "region": "Northern", "lat": 11.9401, "lon": 79.4861, "area": 3725.0, "pop": 2092703},
    {"code": "KLK", "name": "Kallakurichi", "headquarters": "Kallakurichi", "region": "Northern", "lat": 11.7384, "lon": 78.9639, "area": 3520.0, "pop": 1370281},
    {"code": "CUD", "name": "Cuddalore", "headquarters": "Cuddalore", "region": "Central", "lat": 11.7480, "lon": 79.7714, "area": 3678.0, "pop": 2605914},
    {"code": "CBE", "name": "Coimbatore", "headquarters": "Coimbatore", "region": "Western", "lat": 11.0168, "lon": 76.9558, "area": 4723.0, "pop": 3458045},
    {"code": "TPR", "name": "Tiruppur", "headquarters": "Tiruppur", "region": "Western", "lat": 11.1085, "lon": 77.3411, "area": 5186.0, "pop": 2479052},
    {"code": "ERD", "name": "Erode", "headquarters": "Erode", "region": "Western", "lat": 11.3410, "lon": 77.7172, "area": 5722.0, "pop": 2251744},
    {"code": "SLM", "name": "Salem", "headquarters": "Salem", "region": "Western", "lat": 11.6643, "lon": 78.1460, "area": 5245.0, "pop": 3482056},
    {"code": "NKL", "name": "Namakkal", "headquarters": "Namakkal", "region": "Western", "lat": 11.2189, "lon": 78.1674, "area": 3368.0, "pop": 1726601},
    {"code": "KRR", "name": "Karur", "headquarters": "Karur", "region": "Central", "lat": 10.9601, "lon": 78.0766, "area": 2895.0, "pop": 1064493},
    {"code": "DHP", "name": "Dharmapuri", "headquarters": "Dharmapuri", "region": "Western", "lat": 12.1211, "lon": 78.1582, "area": 4498.0, "pop": 1506843},
    {"code": "KRI", "name": "Krishnagiri", "headquarters": "Krishnagiri", "region": "Western", "lat": 12.5186, "lon": 78.2137, "area": 5143.0, "pop": 1879809},
    {"code": "NLG", "name": "Nilgiris", "headquarters": "Udhagamandalam", "region": "Western", "lat": 11.4102, "lon": 76.6950, "area": 2549.0, "pop": 735394},
    {"code": "TRY", "name": "Tiruchirappalli", "headquarters": "Tiruchirappalli", "region": "Central", "lat": 10.7905, "lon": 78.7047, "area": 4403.0, "pop": 2722290},
    {"code": "PER", "name": "Perambalur", "headquarters": "Perambalur", "region": "Central", "lat": 11.2342, "lon": 78.8820, "area": 1757.0, "pop": 565223},
    {"code": "ARI", "name": "Ariyalur", "headquarters": "Ariyalur", "region": "Central", "lat": 11.1400, "lon": 79.0786, "area": 1949.0, "pop": 754894},
    {"code": "PDK", "name": "Pudukkottai", "headquarters": "Pudukkottai", "region": "Central", "lat": 10.3797, "lon": 78.8208, "area": 4663.0, "pop": 1618345},
    {"code": "TNJ", "name": "Thanjavur", "headquarters": "Thanjavur", "region": "Delta", "lat": 10.7870, "lon": 79.1378, "area": 3396.0, "pop": 2405890},
    {"code": "TVR", "name": "Tiruvarur", "headquarters": "Tiruvarur", "region": "Delta", "lat": 10.7725, "lon": 79.6365, "area": 2097.0, "pop": 1264277},
    {"code": "NGP", "name": "Nagapattinam", "headquarters": "Nagapattinam", "region": "Delta", "lat": 10.7672, "lon": 79.8449, "area": 1397.0, "pop": 697061},
    {"code": "MYL", "name": "Mayiladuthurai", "headquarters": "Mayiladuthurai", "region": "Delta", "lat": 11.1035, "lon": 79.6550, "area": 1172.0, "pop": 918356},
    {"code": "MDU", "name": "Madurai", "headquarters": "Madurai", "region": "Southern", "lat": 9.9252, "lon": 78.1198, "area": 3741.0, "pop": 3038252},
    {"code": "DGL", "name": "Dindigul", "headquarters": "Dindigul", "region": "Southern", "lat": 10.3673, "lon": 77.9803, "area": 6266.0, "pop": 2159775},
    {"code": "THN", "name": "Theni", "headquarters": "Theni", "region": "Southern", "lat": 10.0104, "lon": 77.4768, "area": 2889.0, "pop": 1245899},
    {"code": "VRD", "name": "Virudhunagar", "headquarters": "Virudhunagar", "region": "Southern", "lat": 9.5680, "lon": 77.9624, "area": 4241.0, "pop": 1942288},
    {"code": "SVG", "name": "Sivaganga", "headquarters": "Sivaganga", "region": "Southern", "lat": 9.8433, "lon": 78.4809, "area": 4189.0, "pop": 1339101},
    {"code": "RMD", "name": "Ramanathapuram", "headquarters": "Ramanathapuram", "region": "Southern", "lat": 9.3639, "lon": 78.8395, "area": 4104.0, "pop": 1353445},
    {"code": "TNV", "name": "Tirunelveli", "headquarters": "Tirunelveli", "region": "Southern", "lat": 8.7139, "lon": 77.7567, "area": 3842.0, "pop": 1665253},
    {"code": "TKS", "name": "Tenkasi", "headquarters": "Tenkasi", "region": "Southern", "lat": 8.9594, "lon": 77.3150, "area": 2916.0, "pop": 1407627},
    {"code": "TKD", "name": "Thoothukudi", "headquarters": "Thoothukudi", "region": "Southern", "lat": 8.7642, "lon": 78.1348, "area": 4707.0, "pop": 1750176},
    {"code": "KKM", "name": "Kanyakumari", "headquarters": "Nagercoil", "region": "Southern", "lat": 8.0883, "lon": 77.5385, "area": 1672.0, "pop": 1870374}
]

# Sample Key Taluks per Key Urban District
KEY_TALUKS = {
    "CHN": ["Mylapore", "Egmore", "Guindy", "Velachery", "Sholinganallur", "Aminjikarai", "Tondiarpet", "Alandur"],
    "CGL": ["Tambaram", "Pallavaram", "Chengalpattu", "Vandalur", "Thiruporur"],
    "TLR": ["Ambattur", "Poonamallee", "Avadi", "Tiruvallur", "Ponneri"],
    "CBE": ["Coimbatore North", "Coimbatore South", "Sulur", "Pollachi", "Mettupalayam"],
    "MDU": ["Madurai North", "Madurai South", "Thirumangalam", "Melur"],
    "TRY": ["Tiruchirappalli West", "Tiruchirappalli East", "Srirangam", "Lalgudi"],
    "SLM": ["Salem", "Salem South", "Attur", "Omalur"],
    "KRI": ["Hosur", "Krishnagiri", "Denkanikottai"],
    "KCH": ["Kanchipuram", "Sriperumbudur", "Walajabad"]
}

# Key Monitored Real Estate Localities (Core Metro, Suburbs & Industrial Nodes)
MONITORED_LOCALITIES = [
    # Chennai Core & Suburbs
    {"dist": "CHN", "taluk": "Mylapore", "name": "Mylapore", "pin": "600004", "tier": "TIER_1", "lat": 13.0368, "lon": 80.2676},
    {"dist": "CHN", "taluk": "Egmore", "name": "Nungambakkam", "pin": "600034", "tier": "TIER_1", "lat": 13.0569, "lon": 80.2425},
    {"dist": "CHN", "taluk": "Aminjikarai", "name": "Anna Nagar", "pin": "600040", "tier": "TIER_1", "lat": 13.0850, "lon": 80.2101},
    {"dist": "CHN", "taluk": "Guindy", "name": "Adyar", "pin": "600020", "tier": "TIER_1", "lat": 13.0012, "lon": 80.2565},
    {"dist": "CHN", "taluk": "Guindy", "name": "Besant Nagar", "pin": "600090", "tier": "TIER_1", "lat": 13.0003, "lon": 80.2667},
    {"dist": "CHN", "taluk": "Velachery", "name": "Velachery", "pin": "600042", "tier": "TIER_1", "lat": 12.9815, "lon": 80.2180},
    {"dist": "CHN", "taluk": "Sholinganallur", "name": "Sholinganallur (OMR)", "pin": "600119", "tier": "TIER_1", "lat": 12.9010, "lon": 80.2279},
    {"dist": "CHN", "taluk": "Sholinganallur", "name": "Perungudi", "pin": "600096", "tier": "TIER_1", "lat": 12.9654, "lon": 80.2461},
    {"dist": "CHN", "taluk": "Sholinganallur", "name": "Thoraipakkam (OMR)", "pin": "600097", "tier": "TIER_1", "lat": 12.9416, "lon": 80.2362},

    # Chengalpattu / South Chennai Corridors
    {"dist": "CGL", "taluk": "Tambaram", "name": "Tambaram", "pin": "600045", "tier": "TIER_1", "lat": 12.9249, "lon": 80.1000},
    {"dist": "CGL", "taluk": "Pallavaram", "name": "Pallavaram", "pin": "600043", "tier": "TIER_1", "lat": 12.9675, "lon": 80.1491},
    {"dist": "CGL", "taluk": "Thiruporur", "name": "Siruseri (SIPCOT IT)", "pin": "603103", "tier": "TIER_1", "lat": 12.8360, "lon": 80.2180},
    {"dist": "CGL", "taluk": "Chengalpattu", "name": "Mahindra World City", "pin": "603002", "tier": "TIER_2", "lat": 12.7230, "lon": 80.0050},

    # Tiruvallur / West Chennai Corridors
    {"dist": "TLR", "taluk": "Ambattur", "name": "Ambattur Industrial Estate", "pin": "600058", "tier": "TIER_1", "lat": 13.0983, "lon": 80.1620},
    {"dist": "TLR", "taluk": "Poonamallee", "name": "Porur", "pin": "600116", "tier": "TIER_1", "lat": 13.0382, "lon": 80.1565},
    {"dist": "TLR", "taluk": "Avadi", "name": "Avadi", "pin": "600054", "tier": "TIER_1", "lat": 13.1147, "lon": 80.1018},

    # Kanchipuram / Industrial Corridor
    {"dist": "KCH", "taluk": "Sriperumbudur", "name": "Sriperumbudur Industrial Hub", "pin": "602105", "tier": "TIER_2", "lat": 12.9699, "lon": 79.9408},
    {"dist": "KCH", "taluk": "Sriperumbudur", "name": "Parandur (Greenfield Airport Zone)", "pin": "631552", "tier": "TIER_2", "lat": 12.9900, "lon": 79.7900},

    # Coimbatore (Tier 2 Growth Engine)
    {"dist": "CBE", "taluk": "Coimbatore North", "name": "RS Puram", "pin": "641002", "tier": "TIER_2", "lat": 11.0080, "lon": 76.9480},
    {"dist": "CBE", "taluk": "Coimbatore North", "name": "Saravanampatti (IT Corridor)", "pin": "641035", "tier": "TIER_2", "lat": 11.0820, "lon": 76.9950},
    {"dist": "CBE", "taluk": "Coimbatore South", "name": "Peelamedu (Avinashi Road)", "pin": "641004", "tier": "TIER_2", "lat": 11.0280, "lon": 77.0120},
    {"dist": "CBE", "taluk": "Coimbatore South", "name": "Race Course", "pin": "641018", "tier": "TIER_2", "lat": 11.0010, "lon": 76.9740},

    # Madurai
    {"dist": "MDU", "taluk": "Madurai North", "name": "KK Nagar", "pin": "625020", "tier": "TIER_2", "lat": 9.9320, "lon": 78.1500},
    {"dist": "MDU", "taluk": "Madurai South", "name": "Villapuram", "pin": "625012", "tier": "TIER_2", "lat": 9.9010, "lon": 78.1180},

    # Tiruchirappalli
    {"dist": "TRY", "taluk": "Tiruchirappalli West", "name": "Thillai Nagar", "pin": "620018", "tier": "TIER_2", "lat": 10.8280, "lon": 78.6860},
    {"dist": "TRY", "taluk": "Srirangam", "name": "Srirangam", "pin": "620006", "tier": "TIER_2", "lat": 10.8620, "lon": 78.6940},

    # Salem
    {"dist": "SLM", "taluk": "Salem", "name": "Fairlands", "pin": "636016", "tier": "TIER_2", "lat": 11.6780, "lon": 78.1400},

    # Krishnagiri / Hosur (Bangalore Border Tech Corridor)
    {"dist": "KRI", "taluk": "Hosur", "name": "Hosur Sipcot Phase 1 & 2", "pin": "635126", "tier": "TIER_2", "lat": 12.7409, "lon": 77.8253}
]

# Major Tamil Nadu Infrastructure Projects
STRATEGIC_INFRASTRUCTURE = [
    {
        "dist": "CHN", "loc": "Sholinganallur (OMR)",
        "name": "Chennai Metro Phase 2 - Corridor 3 (Madhavaram to SIPCOT)",
        "type": "METRO", "status": "UNDER_CONSTRUCTION",
        "year": 2028, "capex": 61843.0, "radius": 4.0,
        "desc": "118.9 km high-speed mass transit linking North Chennai with OMR IT Corridor."
    },
    {
        "dist": "KCH", "loc": "Parandur (Greenfield Airport Zone)",
        "name": "Chennai Greenfield International Airport (Parandur)",
        "type": "AIRPORT", "status": "ANNOUNCED",
        "year": 2030, "capex": 20000.0, "radius": 20.0,
        "desc": "State-of-the-art 4,700-acre second airport for Chennai with 100M annual passenger capacity."
    },
    {
        "dist": "CGL", "loc": "Mahindra World City",
        "name": "Chennai Peripheral Ring Road (CPRR)",
        "type": "HIGHWAY", "status": "UNDER_CONSTRUCTION",
        "year": 2027, "capex": 12301.0, "radius": 8.0,
        "desc": "133 km 6-lane access-controlled expressway connecting Ennore Port to Mahabalipuram."
    },
    {
        "dist": "CBE", "loc": "Peelamedu (Avinashi Road)",
        "name": "Coimbatore Elevated Expressway & Metro Corridor",
        "type": "METRO", "status": "UNDER_CONSTRUCTION",
        "year": 2027, "capex": 9424.0, "radius": 5.0,
        "desc": "Avinashi Road 10.1 km elevated corridor and proposed mass rapid transit."
    },
    {
        "dist": "KRI", "loc": "Hosur Sipcot Phase 1 & 2",
        "name": "Hosur EV & Advanced Manufacturing Tech Corridor",
        "type": "INDUSTRIAL_CORRIDOR", "status": "OPERATIONAL",
        "year": 2025, "capex": 15000.0, "radius": 15.0,
        "desc": "Global manufacturing cluster hosting major electric vehicle, electronics, and aerospace manufacturing."
    }
]


def seed_geographic_master(db: Session = None):
    """Seed districts, taluks, localities, sources, and property types."""
    engine = get_real_estate_engine()
    Base.metadata.create_all(bind=engine)

    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        # 1. Seed Data Sources
        for code, meta in REAL_ESTATE_SOURCES.items():
            existing_src = db.query(DataSource).filter(DataSource.code == code).first()
            if not existing_src:
                src = DataSource(
                    code=code,
                    name=meta["name"],
                    provider=meta["provider"],
                    access_method=meta["access_method"],
                    url=meta["url"],
                    authentication_required=meta["authentication_required"],
                    update_frequency=meta["update_frequency"],
                    status="ACTIVE",
                    license_notes=meta["license_notes"]
                )
                db.add(src)
        db.flush()

        # 2. Seed Property Types
        for code, meta in PROPERTY_CATEGORIES.items():
            existing_pt = db.query(PropertyType).filter(PropertyType.code == code).first()
            if not existing_pt:
                pt = PropertyType(
                    code=code,
                    category=meta["category"],
                    name=meta["name"],
                    unit_default=meta["unit"],
                    description=f"Standard Tamil Nadu {meta['name']} property asset class."
                )
                db.add(pt)
        db.flush()

        # 3. Seed Districts (All 38)
        district_map = {}
        for d in TAMIL_NADU_DISTRICTS:
            existing_d = db.query(District).filter(District.code == d["code"]).first()
            if not existing_d:
                dist = District(
                    code=d["code"],
                    name=d["name"],
                    headquarters=d["headquarters"],
                    region=d["region"],
                    latitude=d["lat"],
                    longitude=d["lon"],
                    area_sqkm=d["area"],
                    population_census=d["pop"]
                )
                db.add(dist)
                db.flush()
                district_map[d["code"]] = dist.id
            else:
                district_map[d["code"]] = existing_d.id

        # 4. Seed Taluks
        taluk_map = {}
        for dist_code, taluk_names in KEY_TALUKS.items():
            dist_id = district_map.get(dist_code)
            if not dist_id:
                continue
            for t_name in taluk_names:
                existing_t = db.query(Taluk).filter(
                    Taluk.district_id == dist_id,
                    Taluk.name == t_name
                ).first()
                if not existing_t:
                    tal = Taluk(district_id=dist_id, name=t_name)
                    db.add(tal)
                    db.flush()
                    taluk_map[(dist_code, t_name)] = tal.id
                else:
                    taluk_map[(dist_code, t_name)] = existing_t.id

        # Also create a default/headquarters taluk for districts without explicit taluks in KEY_TALUKS
        for d in TAMIL_NADU_DISTRICTS:
            dist_code = d["code"]
            dist_id = district_map[dist_code]
            if dist_code not in KEY_TALUKS:
                t_name = f"{d['name']} Taluk"
                existing_t = db.query(Taluk).filter(
                    Taluk.district_id == dist_id,
                    Taluk.name == t_name
                ).first()
                if not existing_t:
                    tal = Taluk(district_id=dist_id, name=t_name)
                    db.add(tal)
                    db.flush()
                    taluk_map[(dist_code, t_name)] = tal.id

        # 5. Seed Monitored Localities
        locality_map = {}
        for loc in MONITORED_LOCALITIES:
            dist_id = district_map.get(loc["dist"])
            tal_id = taluk_map.get((loc["dist"], loc["taluk"]))
            if not dist_id:
                continue
            existing_loc = db.query(Locality).filter(
                Locality.district_id == dist_id,
                Locality.name == loc["name"]
            ).first()
            if not existing_loc:
                loc_obj = Locality(
                    district_id=dist_id,
                    taluk_id=tal_id,
                    name=loc["name"],
                    postal_code=loc["pin"],
                    tier=loc["tier"],
                    latitude=loc["lat"],
                    longitude=loc["lon"]
                )
                db.add(loc_obj)
                db.flush()
                locality_map[loc["name"]] = loc_obj.id
            else:
                locality_map[loc["name"]] = existing_loc.id

        # 6. Seed Infrastructure Projects
        for proj in STRATEGIC_INFRASTRUCTURE:
            dist_id = district_map.get(proj["dist"])
            loc_id = locality_map.get(proj["loc"])
            existing_proj = db.query(InfrastructureProject).filter(
                InfrastructureProject.project_name == proj["name"]
            ).first()
            if not existing_proj:
                ip = InfrastructureProject(
                    district_id=dist_id,
                    locality_id=loc_id,
                    project_name=proj["name"],
                    project_type=proj["type"],
                    status=proj["status"],
                    expected_completion_year=proj["year"],
                    investment_inr_crores=proj["capex"],
                    impact_radius_km=proj["radius"],
                    description=proj["desc"]
                )
                db.add(ip)

        db.commit()
        print(f"Successfully seeded statewide geographic master: {len(district_map)} districts, {len(taluk_map)} taluks, {len(locality_map)} localities.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    seed_geographic_master()

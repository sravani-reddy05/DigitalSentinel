import json

from database.db import (
    get_connection,
    initialize_database
)


def seed_database():

    initialize_database()

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # -------------------------------------
        # 1. Insert five fictional, clearly labelled sample brands
        # -------------------------------------

        sample_brands = [
            ("Northstar Outfitters (Demo)", "https://northstar.example.com", "Fictional outdoor apparel company for demonstrations."),
            ("LumaPay (Demo)", "https://lumapay.example.com", "Fictional digital payments company for demonstrations."),
            ("Verdant Foods (Demo)", "https://verdantfoods.example.com", "Fictional sustainable grocery company for demonstrations."),
            ("Aster Mobile (Demo)", "https://astermobile.example.com", "Fictional consumer electronics company for demonstrations."),
            ("BluePeak Health (Demo)", "https://bluepeakhealth.example.com", "Fictional wellness company for demonstrations."),
        ]
        brand_ids = {}
        for brand_name, website, description in sample_brands:
            cursor.execute("SELECT id FROM brand_profiles WHERE brand_name = ?", (brand_name,))
            existing = cursor.fetchone()
            if existing:
                brand_ids[brand_name] = existing["id"]
            else:
                cursor.execute("INSERT INTO brand_profiles (brand_name, official_website, description) VALUES (?, ?, ?)", (brand_name, website, description))
                brand_ids[brand_name] = cursor.lastrowid
        brand_id = brand_ids[sample_brands[0][0]]

        # -------------------------------------
        # 2. Insert approved official assets
        # -------------------------------------

        official_assets = [
            (
                brand_id,
                "social_profile",
                "Instagram",
                "adidas",
                "https://www.instagram.com/adidas/",
                "Adidas",
                1
            ),
            (
                brand_id,
                "application",
                "App Store",
                "Adidas Official",
                "",
                "Adidas",
                1
            )
        ]

        for asset in official_assets:

            cursor.execute("""
                SELECT id
                FROM official_assets
                WHERE brand_id = ?
                  AND asset_type = ?
                  AND platform = ?
                  AND asset_name = ?
            """, (
                asset[0],
                asset[1],
                asset[2],
                asset[3]
            ))

            if not cursor.fetchone():

                cursor.execute("""
                    INSERT INTO official_assets (
                        brand_id,
                        asset_type,
                        platform,
                        asset_name,
                        asset_url,
                        publisher,
                        verified
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, asset)

        # -------------------------------------
        # 3. Insert fictional detection examples
        # -------------------------------------

        examples = [
            {
                "target_name": "adidas_offers_50",
                "platform": "Instagram",
                "target_url": "",
                "publisher": "",
                "description": (
                    "Fictional demonstration account "
                    "advertising unusually large discounts."
                ),
                "name_similarity": 70,
                "risk_score": 78,
                "risk_level": "High",
                "reasons": [
                    "Similar brand name",
                    "Additional promotional words",
                    "Requires manual verification"
                ],
                "status": "Needs Review"
            },
            {
                "target_name": "Adidas Sports Deals",
                "platform": "App Store",
                "target_url": "",
                "publisher": "Example Publisher",
                "description": (
                    "Fictional application record for testing."
                ),
                "name_similarity": 55,
                "risk_score": 55,
                "risk_level": "Medium",
                "reasons": [
                    "Brand-like application name",
                    "Publisher requires verification"
                ],
                "status": "Needs Review"
            }
        ]

        for example in examples:

            cursor.execute("""
                SELECT id
                FROM detections
                WHERE brand_id = ?
                  AND target_name = ?
                  AND platform = ?
            """, (
                brand_id,
                example["target_name"],
                example["platform"]
            ))

            if cursor.fetchone():
                continue

            cursor.execute("""
                INSERT INTO detections (
                    brand_id,
                    target_name,
                    platform,
                    target_url,
                    publisher,
                    description,
                    name_similarity,
                    risk_score,
                    risk_level,
                    reasons,
                    status,
                    is_official
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                brand_id,
                example["target_name"],
                example["platform"],
                example["target_url"],
                example["publisher"],
                example["description"],
                example["name_similarity"],
                example["risk_score"],
                example["risk_level"],
                json.dumps(example["reasons"]),
                example["status"],
                0
            ))

        connection.commit()

        print("DigitalSentinel sample data inserted successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()

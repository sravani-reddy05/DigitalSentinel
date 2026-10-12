from database.db import get_connection


def create_brand(
    brand_name,
    official_website="",
    description=""
):
    """Create a new brand profile."""

    if not brand_name or not brand_name.strip():
        raise ValueError("Brand name is required.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO brand_profiles (
                brand_name,
                official_website,
                description
            )
            VALUES (?, ?, ?)
        """, (
            brand_name.strip(),
            official_website.strip(),
            description.strip()
        ))

        brand_id = cursor.lastrowid

        connection.commit()

        return brand_id

    finally:
        connection.close()


def get_brand(brand_id=None):
    """Retrieve a brand by ID or get the latest brand."""

    connection = get_connection()

    try:
        if brand_id is not None:

            cursor = connection.execute("""
                SELECT *
                FROM brand_profiles
                WHERE id = ?
            """, (brand_id,))

        else:

            cursor = connection.execute("""
                SELECT *
                FROM brand_profiles
                ORDER BY id DESC
                LIMIT 1
            """)

        row = cursor.fetchone()

        return dict(row) if row else None

    finally:
        connection.close()


def get_all_brands():
    """Retrieve all registered brand profiles."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT *
            FROM brand_profiles
            ORDER BY id DESC
        """)

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


def set_brand_logo(brand_id, logo_path):
    connection = get_connection()
    try:
        cursor = connection.execute(
            "UPDATE brand_profiles SET logo_path = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (logo_path, brand_id),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def update_brand(
    brand_id,
    brand_name,
    official_website="",
    description=""
):
    """Update an existing brand profile."""

    if not brand_name or not brand_name.strip():
        raise ValueError("Brand name is required.")

    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE brand_profiles
            SET
                brand_name = ?,
                official_website = ?,
                description = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            brand_name.strip(),
            official_website.strip(),
            description.strip(),
            brand_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()


def add_official_asset(
    brand_id,
    asset_type,
    platform,
    asset_name,
    asset_url="",
    publisher=""
):
    """Register an official account or application."""

    if not asset_name or not asset_name.strip():
        raise ValueError("Asset name is required.")

    connection = get_connection()

    try:
        cursor = connection.execute("""
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
        """, (
            brand_id,
            asset_type,
            platform,
            asset_name.strip(),
            asset_url.strip(),
            publisher.strip(),
            0
        ))

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_official_assets(brand_id):
    """Return official assets belonging to a brand."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            SELECT *
            FROM official_assets
            WHERE brand_id = ?
            ORDER BY id DESC
        """, (brand_id,))

        return [
            dict(row)
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


def verify_official_asset(asset_id):
    """Mark an asset as approved after verification."""

    connection = get_connection()

    try:
        cursor = connection.execute("""
            UPDATE official_assets
            SET verified = 1
            WHERE id = ?
        """, (asset_id,))

        connection.commit()

        return cursor.rowcount > 0

    finally:
        connection.close()

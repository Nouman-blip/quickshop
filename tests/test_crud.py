import pytest
from datetime import datetime
from app import crud, models, schemas
from app.core.sustainability import SustainabilityService

def test_get_eco_certified_products(db_session):
    # Create test products
    eco_product1 = models.Product(
        name="Eco Bottle",
        price=19.99,
        eco_certified=True,
        sustainability_score=80.0
    )
    eco_product2 = models.Product(
        name="Regular Bottle",
        price=9.99,
        eco_certified=True,
        sustainability_score=45.0
    )
    db_session.add_all([eco_product1, eco_product2])
    db_session.commit()

    # Test with minimum score filter
    products = crud.get_eco_certified_products(db_session, min_score=50.0)
    assert len(products) == 1
    assert products[0].name == "Eco Bottle"

def test_get_locally_sourced_products(db_session):
    # Create test products
    local_product = models.Product(
        name="Local Produce",
        price=5.99,
        locally_sourced=True,
        source_region="Northwest"
    )
    non_local = models.Product(
        name="Imported Produce",
        price=4.99,
        locally_sourced=False
    )
    db_session.add_all([local_product, non_local])
    db_session.commit()

    # Test region filter
    products = crud.get_locally_sourced_products(db_session, region="Northwest")
    assert len(products) == 1
    assert products[0].name == "Local Produce"

def test_get_sustainable_products(db_session):
    # Create test products
    sustainable_product = models.Product(
        name="Eco Pack",
        sustainability_score=85.0,
        eco_certified=True,
        biodegradable=True
    )
    regular_product = models.Product(
        name="Regular Pack",
        sustainability_score=65.0,
        eco_certified=False,
        biodegradable=False
    )
    db_session.add_all([sustainable_product, regular_product])
    db_session.commit()

    # Test with multiple filters
    products = crud.get_sustainable_products(
        db_session,
        min_score=70.0,
        eco_certified=True,
        biodegradable=True
    )
    assert len(products) == 1
    assert products[0].name == "Eco Pack"

def test_get_product_impact(db_session):
    # Create test product with impact metrics
    product = models.Product(
        name="Green Product",
        carbon_footprint=10.5,
        water_savings=100.0,
        recycled_content=75.0,
        sustainability_score=90.0,
        eco_certifications=["Green Seal", "Energy Star"],
        renewable_materials_percentage=80.0
    )
    db_session.add(product)
    db_session.commit()

    # Test impact data retrieval
    impact = crud.get_product_impact(db_session, product.id)
    assert impact is not None
    assert impact["carbon_footprint"] == 10.5
    assert impact["sustainability_score"] == 90.0
    assert "Green Seal" in impact["eco_certifications"]

def test_eco_certified_products_with_empty_result(db_session):
    # Test when no products meet the criteria
    eco_product = models.Product(
        name="Low Score Eco Product",
        price=15.99,
        eco_certified=True,
        sustainability_score=30.0
    )
    db_session.add(eco_product)
    db_session.commit()

    products = crud.get_eco_certified_products(db_session, min_score=75.0)
    assert len(products) == 0

def test_locally_sourced_products_multiple_regions(db_session):
    # Test products from different regions
    products = [
        models.Product(
            name="Northwest Apples",
            price=3.99,
            locally_sourced=True,
            source_region="Northwest"
        ),
        models.Product(
            name="Southwest Oranges",
            price=4.99,
            locally_sourced=True,
            source_region="Southwest"
        )
    ]
    db_session.add_all(products)
    db_session.commit()

    northwest_products = crud.get_locally_sourced_products(db_session, region="Northwest")
    assert len(northwest_products) == 1
    assert northwest_products[0].name == "Northwest Apples"

def test_sustainable_products_partial_criteria(db_session):
    # Test products meeting some but not all criteria
    product = models.Product(
        name="Partially Eco Product",
        sustainability_score=75.0,
        eco_certified=True,
        biodegradable=False
    )
    db_session.add(product)
    db_session.commit()

    # Should find product when only checking score and eco_certified
    products = crud.get_sustainable_products(
        db_session,
        min_score=70.0,
        eco_certified=True
    )
    assert len(products) == 1

    # Should not find product when all criteria are required
    products = crud.get_sustainable_products(
        db_session,
        min_score=70.0,
        eco_certified=True,
        biodegradable=True
    )
    assert len(products) == 0

def test_product_impact_not_found(db_session):
    # Test impact retrieval for non-existent product
    impact = crud.get_product_impact(db_session, product_id=999)
    assert impact is None
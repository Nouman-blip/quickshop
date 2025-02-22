import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Product
from decimal import Decimal

client = TestClient(app)

def test_list_eco_certified_products_endpoint(db_session):
    # Setup test data
    products = [
        Product(
            name="Premium Eco Bottle",
            price=Decimal("24.99"),
            eco_certified=True,
            sustainability_score=95.0,
            carbon_footprint=5.2,
            water_savings=150.0
        ),
        Product(
            name="Standard Bottle",
            price=Decimal("14.99"),
            eco_certified=False,
            sustainability_score=40.0
        )
    ]
    db_session.add_all(products)
    db_session.commit()

    response = client.get("/products/eco-certified?min_score=90")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Premium Eco Bottle"
    assert data[0]["sustainability_score"] == 95.0

def test_get_product_environmental_impact(db_session):
    product = Product(
        name="Bamboo Toothbrush",
        price=Decimal("4.99"),
        eco_certified=True,
        carbon_footprint=1.2,
        water_savings=50.0,
        recycled_content=100.0,
        biodegradable=True
    )
    db_session.add(product)
    db_session.commit()

    response = client.get(f"/products/impact/{product.id}")
    assert response.status_code == 200
    impact = response.json()
    assert impact["carbon_footprint"] == 1.2
    assert impact["recycled_content"] == 100.0
    assert impact["water_savings"] == 50.0

def test_filter_sustainable_products(db_session):
    products = [
        Product(
            name="Eco-friendly Soap",
            price=Decimal("3.99"),
            sustainability_score=85.0,
            biodegradable=True,
            eco_certified=True
        ),
        Product(
            name="Regular Soap",
            price=Decimal("2.99"),
            sustainability_score=45.0,
            biodegradable=False,
            eco_certified=False
        )
    ]
    db_session.add_all(products)
    db_session.commit()

    response = client.get(
        "/products/sustainable?min_score=80&biodegradable=true&eco_certified=true"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Eco-friendly Soap"
    def test_product_impact_not_found(db_session):
        response = client.get("/products/impact/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product impact data not found"
    
    def test_filter_products_by_packaging_type(db_session):
        products = [
            Product(
                name="Zero Waste Shampoo",
                price=Decimal("12.99"),
                packaging_type="BIODEGRADABLE",
                sustainability_score=88.0,
                eco_certified=True
            ),
            Product(
                name="Reusable Container",
                price=Decimal("9.99"),
                packaging_type="REUSABLE",
                sustainability_score=92.0,
                eco_certified=True
            )
        ]
        db_session.add_all(products)
        db_session.commit()
    
        response = client.get("/products/packaging/biodegradable")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Zero Waste Shampoo"
    
    def test_combined_eco_filters(db_session):
        product = Product(
            name="Ultimate Eco Product",
            price=Decimal("29.99"),
            eco_certified=True,
            biodegradable=True,
            locally_sourced=True,
            sustainability_score=98.0,
            source_region="Northwest",
            carbon_footprint=0.5
        )
        db_session.add(product)
        db_session.commit()
    
        response = client.get(
            "/products/sustainable?"
            "min_score=95&"
            "eco_certified=true&"
            "biodegradable=true&"
            "region=Northwest"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sustainability_score"] == 98.0
    def test_invalid_packaging_type(db_session):
        response = client.get("/products/packaging/INVALID_TYPE")
        assert response.status_code == 422
        assert "Invalid packaging type" in response.json()["detail"]
    def test_sustainability_score_calculation(db_session):
        product_data = {
            "name": "Auto-scored Product",
            "price": "19.99",
            "eco_certified": True,
            "biodegradable": True,
            "locally_sourced": True,
            "is_recyclable": True
        }
        
        response = client.post("/products/", json=product_data)
        assert response.status_code == 201
        data = response.json()
        # Should calculate maximum score based on all eco-friendly attributes
        assert data["sustainability_score"] == 100.0
    def test_filter_products_with_multiple_regions(db_session):
        products = [
            Product(
                name="Northwest Produce",
                price=Decimal("7.99"),
                locally_sourced=True,
                source_region="Northwest",
                sustainability_score=88.0
            ),
            Product(
                name="Southwest Produce",
                price=Decimal("6.99"),
                locally_sourced=True,
                source_region="Southwest",
                sustainability_score=85.0
            )
        ]
        db_session.add_all(products)
        db_session.commit()
    
        response = client.get("/products/local-sourced?region=Northwest,Southwest")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        regions = [product["source_region"] for product in data]
        assert "Northwest" in regions
        assert "Southwest" in regions
    def test_update_product_eco_metrics(db_session):
        product = Product(
            name="Updatable Eco Product",
            price=Decimal("15.99"),
            eco_certified=False,
            sustainability_score=50.0
        )
        db_session.add(product)
        db_session.commit()
    def test_eco_metrics_validation(db_session):
        invalid_product_data = {
            "name": "Invalid Eco Product",
            "price": "25.99",
            "sustainability_score": 150.0,  # Invalid: over 100
            "water_savings": -10.0  # Invalid: negative value
        }
        
        response = client.post("/products/", json=invalid_product_data)
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("sustainability_score" in error["loc"] for error in errors)
        assert any("water_savings" in error["loc"] for error in errors)
    def test_eco_product_search(db_session):
        products = [
            Product(
                name="Eco-friendly Water Bottle",
                price=Decimal("15.99"),
                eco_certified=True,
                sustainability_score=90.0
            ),
            Product(
                name="Water Bottle",
                price=Decimal("10.99"),
                eco_certified=False,
                sustainability_score=40.0
            )
        ]
        db_session.add_all(products)
        db_session.commit()
    
        # Add missing test implementation
        response = client.get("/products/search?query=water+bottle&eco_only=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Eco-friendly Water Bottle"

    def test_eco_product_statistics(db_session):
        products = [
            Product(
                name="Eco Product 1",
                price=Decimal("20.99"),
                eco_certified=True,
                sustainability_score=95.0,
                carbon_footprint=2.0
            ),
            Product(
                name="Eco Product 2",
                price=Decimal("15.99"),
                eco_certified=True,
                sustainability_score=85.0,
                carbon_footprint=3.0
            )
        ]
        db_session.add_all(products)
        db_session.commit()
    
        response = client.get("/products/eco-statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["average_sustainability_score"] == 90.0
        assert stats["total_carbon_footprint"] == 5.0
        assert stats["eco_certified_count"] == 2
    def test_eco_metrics_trends(db_session):
        product = Product(
            name="Trend Analysis Product",
            price=Decimal("24.99"),
            sustainability_score=75.0,
            carbon_footprint=4.0
        )
        db_session.add(product)
        db_session.commit()
    
        # Simulate multiple updates to track trends
        updates = [
            {"carbon_footprint": 3.5, "sustainability_score": 80.0},
            {"carbon_footprint": 3.0, "sustainability_score": 85.0},
            {"carbon_footprint": 2.5, "sustainability_score": 90.0}
        ]
        
        for update in updates:
            response = client.patch(f"/products/{product.id}/eco-metrics", json=update)
            assert response.status_code == 200
    
        response = client.get(f"/products/{product.id}/eco-trends")
        assert response.status_code == 200
        trends = response.json()
        assert trends["carbon_footprint_trend"] == "decreasing"
        assert trends["sustainability_trend"] == "improving"
        assert "trend_period_days" in trends
    def test_eco_impact_forecast(db_session):
        product = Product(
            name="Impact Forecast Test",
            price=Decimal("34.99"),
            carbon_footprint=6.0,
            water_savings=80.0,
            sales_volume=100
        )
        db_session.add(product)
        db_session.commit()
    
        response = client.get(f"/products/{product.id}/impact-forecast?months=6")
        assert response.status_code == 200
        forecast = response.json()
        assert "projected_carbon_savings" in forecast
        assert "projected_water_savings" in forecast
        assert "confidence_score" in forecast
    def test_sustainability_recommendations(db_session):
        product = Product(
            name="Improvement Candidate",
            price=Decimal("45.99"),
            sustainability_score=65.0,
            packaging_type="MINIMAL",
            recycled_content=40.0
        )
        db_session.add(product)
        db_session.commit()
    
        response = client.get(f"/products/{product.id}/sustainability-recommendations")
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations["improvement_areas"]) > 0
        assert "estimated_score_impact" in recommendations
        assert "implementation_difficulty" in recommendations
    def test_eco_product_bulk_update(db_session):
        products = [
            Product(
                name=f"Bulk Update Product {i}",
                price=Decimal("19.99"),
                eco_certified=False,
                sustainability_score=50.0
            ) for i in range(3)
        ]
        db_session.add_all(products)
        db_session.commit()
    
        update_data = {
            "ids": [p.id for p in products],
            "eco_certified": True,
            "biodegradable": True
        }
    
        response = client.put("/products/eco-bulk-update", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(p["eco_certified"] for p in data)
        assert all(p["biodegradable"] for p in data)
    
    def test_eco_certification_validation(db_session):
        product_data = {
            "name": "Invalid Certification",
            "price": "29.99",
            "eco_certified": True,
            "eco_certifications": ["Invalid Cert"]  # Should be from valid list
        }
        
        response = client.post("/products/", json=product_data)
        assert response.status_code == 422
        assert "Invalid certification type" in response.json()["detail"]
    
    def test_sustainability_score_recalculation(db_session):
        product = Product(
            name="Score Update Test",
            price=Decimal("25.99"),
            eco_certified=True,
            sustainability_score=70.0
        )
        db_session.add(product)
        db_session.commit()
    
        # Adding more eco-friendly attributes should increase score
        update_data = {
            "biodegradable": True,
            "locally_sourced": True,
            "recycled_content": 95.0
        }
    
        response = client.patch(f"/products/{product.id}/eco-metrics", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["sustainability_score"] > 70.0
        def test_eco_metrics_threshold_alerts(db_session):
            product = Product(
                name="Alert Test Product",
                price=Decimal("29.99"),
                carbon_footprint=15.0,  # High carbon footprint
                water_savings=5.0,      # Low water savings
                sustainability_score=30.0
            )
            db_session.add(product)
            db_session.commit()
        
            response = client.get(f"/products/{product.id}/eco-alerts")
            assert response.status_code == 200
            alerts = response.json()
            assert "high_carbon_footprint" in alerts["warnings"]
            assert "low_water_savings" in alerts["warnings"]
            assert "low_sustainability_score" in alerts["warnings"]
        def test_eco_comparison(db_session):
            products = [
                Product(
                    name="Eco Product A",
                    price=Decimal("25.99"),
                    sustainability_score=90.0,
                    carbon_footprint=2.0
                ),
                Product(
                    name="Eco Product B",
                    price=Decimal("23.99"),
                    sustainability_score=85.0,
                    carbon_footprint=3.0
                )
            ]
            db_session.add_all(products)
            db_session.commit()
        
            response = client.get(f"/products/compare?ids={products[0].id},{products[1].id}")
            assert response.status_code == 200
            comparison = response.json()
            assert "sustainability_difference" in comparison
            assert "carbon_footprint_difference" in comparison
            assert comparison["more_sustainable_product"] == "Eco Product A"
        def test_eco_category_statistics(db_session):
            products = [
                Product(
                    name="Category Test 1",
                    category_id=1,
                    sustainability_score=88.0,
                    eco_certified=True
                ),
                Product(
                    name="Category Test 2",
                    category_id=1,
                    sustainability_score=92.0,
                    eco_certified=True
                )
            ]
            db_session.add_all(products)
            db_session.commit()
        
            response = client.get("/products/category/1/eco-stats")
            assert response.status_code == 200
            stats = response.json()
            assert stats["average_sustainability_score"] == 90.0
            assert stats["eco_certified_percentage"] == 100.0
        def test_eco_metrics_history(db_session):
            product = Product(
                name="Metrics History Test",
                price=Decimal("18.99"),
                carbon_footprint=5.0
            )
            db_session.add(product)
            db_session.commit()
        
            response = client.get(f"/products/{product.id}/eco-metrics/history")
            assert response.status_code == 200
            history = response.json()
            assert "carbon_footprint_history" in history
            assert "sustainability_score_history" in history
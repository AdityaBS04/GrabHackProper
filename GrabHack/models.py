"""
Data models and configurations for the Grab customer service orchestration system
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List


class GrabService(Enum):
    """Grab service types"""
    GRAB_FOOD = "grab_food"
    GRAB_MART = "grab_mart" 
    GRAB_CABS = "grab_cabs"
    GRAB_EXPRESS = "grab_express"


class Actor(Enum):
    """Actor types within each service"""
    # Grab Cabs actors
    DRIVER = "driver"
    CUSTOMER = "customer"
    
    # Grab Food actors
    RESTAURANT = "restaurant"
    DELIVERY_AGENT = "delivery_agent"
    
    # Grab Mart actors
    DARK_HOUSE = "dark_house"
    
    # Grab Express actors
    EXPRESS_DELIVERY_PARTNER = "express_delivery_partner"


class IssueCategory(Enum):
    """Main issue categories across all Grab services"""
    # Common categories
    ORDER_NOT_RECEIVED = "1"
    PORTION_INADEQUATE = "2"
    SAFETY_INCIDENT = "3"
    ITEMS_MISSING = "4"
    POOR_QUALITY = "5"
    SPILLAGE = "6"
    FRAUD = "7"
    COUPON_QUERY = "8"
    PAYMENT_BILLING = "9"
    
    # Grab Cabs specific
    RIDE_ISSUES = "10"
    DRIVER_BEHAVIOR = "11"
    VEHICLE_CONDITION = "12"
    
    # Grab Mart specific  
    PRODUCT_QUALITY = "13"
    SUBSTITUTION_ISSUES = "14"
    STORE_UNAVAILABLE = "15"
    
    # Grab Food Restaurant operational issues
    LONG_WAITING_TIME = "16"
    NOT_ENOUGH_DELIVERY_PARTNERS = "17"
    UNEXPECTED_HINDRANCE = "18"
    RESTAURANT_CUSTOMIZING_ORDER = "19"
    
    # Grab Food Customer operational issues
    RESTAURANT_DELAYS_CANCELLATIONS = "20"
    DELIVERY_PARTNER_NOSHOW = "21"
    ROUTING_TRACKING_ISSUES = "22"
    INVENTORY_ITEM_MISMATCH = "23"
    
    # Grab Food Delivery Agent operational issues
    INCORRECT_CUSTOMER_ADDRESS = "24"
    GPS_APP_TECHNICAL_ISSUES = "25"
    CUSTOMER_LOCATION_DIFFICULTY = "26"
    TRAFFIC_DELAYS = "27"
    VEHICLE_BREAKDOWN = "28"
    SAFETY_ACCIDENT_ENROUTE = "29"
    ORDER_BATCHING_CONFUSION = "30"
    PACKAGE_TAMPERED_SPILLED = "31"
    WRONG_PACKAGE_HANDOVER = "32"
    PAYMENT_COLLECTION_COD = "33"
    CUSTOMER_UNAVAILABLE_DELIVERY = "34"
    LONG_WAIT_CUSTOMER_LOCATION = "35"
    CUSTOMER_LATE_CANCELLATION = "36"
    
    # Grab Express specific issues
    PACKAGE_SIZE_VEHICLE_MISMATCH = "37"
    EXPRESS_DELIVERY_URGENCY = "38"
    VEHICLE_TYPE_REQUIREMENTS = "39"


@dataclass
class SubIssue:
    """Sub-issue with associated tool name, service, and actor"""
    name: str
    tool_name: str
    description: str
    service: GrabService
    actor: Actor
    handler_module: str


# Actor-based issue mappings for Grab Food
GRAB_FOOD_ISSUES = {
    # Order Accuracy & Quality Issues
    IssueCategory.ITEMS_MISSING: [
        SubIssue("Missing items in delivery", "handle_missing_items", "Customer missing items resolution", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.order_quality_handler")
    ],
    IssueCategory.POOR_QUALITY: [
        SubIssue("Wrong item delivered", "handle_wrong_item", "Customer wrong item resolution", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.order_quality_handler"),
        SubIssue("Expired/damaged/poor quality items", "handle_quality_issues", "Customer quality guarantee", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.order_quality_handler"),
    ],
    IssueCategory.PORTION_INADEQUATE: [
        SubIssue("Substituted item not acceptable", "handle_substitution_issues", "Customer substitution preference", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.order_quality_handler"),
        SubIssue("Quantity mismatch", "handle_quantity_mismatch", "Customer quantity accuracy", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.order_quality_handler")
    ],
    
    # Delivery Experience Issues  
    IssueCategory.ORDER_NOT_RECEIVED: [
        SubIssue("Delay beyond promised time", "handle_delivery_delay", "Customer delivery delay compensation", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.delivery_experience_handler"),
        SubIssue("Partial order delivered", "handle_partial_delivery", "Customer partial order resolution", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.delivery_experience_handler"),
    ],
    IssueCategory.SPILLAGE: [
        SubIssue("Cold/frozen items melted or leaked", "handle_temperature_issues", "Customer temperature control guarantee", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.delivery_experience_handler"),
        SubIssue("Package tampered or unsealed", "handle_package_tampering", "Customer package security guarantee", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.delivery_experience_handler"),
    ],
    IssueCategory.ROUTING_TRACKING_ISSUES: [
        SubIssue("Multiple deliveries for same order", "handle_multiple_deliveries", "Customer delivery consolidation", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.delivery_experience_handler")
    ],
    
    # Driver Interaction Issues
    IssueCategory.DRIVER_BEHAVIOR: [
        SubIssue("Rude behavior from delivery partner", "handle_rude_behavior", "Customer professional service standards", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.driver_interaction_handler"),
        SubIssue("Driver unable to find address, keeps calling", "handle_location_difficulty", "Customer navigation assistance", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.driver_interaction_handler"),
    ],
    IssueCategory.FRAUD: [
        SubIssue("Driver asks for extra money (COD manipulation)", "handle_payment_manipulation", "Customer payment protection", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.driver_interaction_handler"),
        SubIssue("Driver marks delivered but no package received", "handle_false_delivery", "Customer delivery verification", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.driver_interaction_handler"),
    ],
    
    # Payment & Refund Issues
    IssueCategory.PAYMENT_BILLING: [
        SubIssue("Double charge for single order", "handle_double_charge", "Customer billing error resolution", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.payment_refund_handler"),
        SubIssue("Failed payment but money deducted", "handle_failed_payment_money_deducted", "Customer payment error resolution", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.payment_refund_handler"),
        SubIssue("COD order marked prepaid", "handle_cod_marked_prepaid", "Customer payment method correction", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.payment_refund_handler"),
        SubIssue("Refund not initiated for missing/damaged items", "handle_refund_not_initiated", "Customer refund processing", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.payment_refund_handler"),
    ],
    
    # Technical Issues
    IssueCategory.COUPON_QUERY: [
        SubIssue("Order auto-cancelled without reason", "handle_auto_cancellation", "Customer system error resolution", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.technical_handler"),
        SubIssue("App shows delivered but not received", "handle_delivery_status_error", "Customer delivery status correction", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.technical_handler"),
        SubIssue("Wrong tracking status", "handle_tracking_status_error", "Customer tracking accuracy", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.technical_handler"),
        SubIssue("Coupons/offers not applied correctly", "handle_coupon_offers_error", "Customer promotional savings", GrabService.GRAB_FOOD, Actor.CUSTOMER, "grab_food.customer.technical_handler"),
    ],
}

# Actor-based issue mappings for Restaurant
GRAB_FOOD_RESTAURANT_ISSUES = {
    IssueCategory.PORTION_INADEQUATE: [
        SubIssue("Restaurant portion violation", "handle_restaurant_portion_violation", "Restaurant portion standards enforcement", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler")
    ],
    IssueCategory.POOR_QUALITY: [
        SubIssue("Restaurant food safety", "handle_restaurant_food_safety", "Restaurant food safety compliance", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler"),
        SubIssue("Restaurant preparation delays", "handle_restaurant_preparation_delays", "Restaurant efficiency optimization", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler"),
        SubIssue("Restaurant ingredient quality", "handle_restaurant_ingredient_quality", "Restaurant ingredient quality standards", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler"),
        SubIssue("Restaurant order accuracy", "handle_restaurant_order_accuracy", "Restaurant order fulfillment quality", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler"),
    ],
    IssueCategory.LONG_WAITING_TIME: [
        SubIssue("Restaurant waiting time optimization", "handle_long_waiting_time", "Restaurant order preparation efficiency", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler")
    ],
    IssueCategory.NOT_ENOUGH_DELIVERY_PARTNERS: [
        SubIssue("Restaurant delivery partner shortage", "handle_delivery_partner_shortage", "Restaurant delivery coordination", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler")
    ],
    IssueCategory.UNEXPECTED_HINDRANCE: [
        SubIssue("Restaurant operational hindrance", "handle_unexpected_hindrance", "Restaurant crisis management", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler")
    ],
    IssueCategory.RESTAURANT_CUSTOMIZING_ORDER: [
        SubIssue("Restaurant order customization", "handle_order_customization", "Restaurant order modification management", GrabService.GRAB_FOOD, Actor.RESTAURANT, "grab_food.restaurant.restaurant_handler")
    ],
}

# Actor-based issue mappings for Delivery Agent
GRAB_FOOD_DELIVERY_ISSUES = {
    # Technical Issues
    IssueCategory.ORDER_NOT_RECEIVED: [
        SubIssue("Delivery time performance", "handle_technical", "Delivery agent time optimization", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.technical_handler"),
        SubIssue("Delivery accuracy issues", "handle_technical", "Delivery agent accuracy improvement", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.technical_handler"),
    ],
    IssueCategory.POOR_QUALITY: [
        SubIssue("Delivery communication", "handle_technical", "Delivery agent communication excellence", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.technical_handler"),
        SubIssue("Delivery safety protocols", "handle_technical", "Delivery agent safety compliance", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.technical_handler"),
        SubIssue("Delivery equipment maintenance", "handle_technical", "Delivery agent equipment standards", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.technical_handler"),
    ],
    # Navigation & Location Issues
    IssueCategory.INCORRECT_CUSTOMER_ADDRESS: [
        SubIssue("Incorrect customer address resolution", "handle_navigation_location", "Delivery agent address verification support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.navigation_location_handler")
    ],
    IssueCategory.GPS_APP_TECHNICAL_ISSUES: [
        SubIssue("GPS and app technical support", "handle_navigation_location", "Delivery agent GPS technical issue resolution", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.navigation_location_handler")
    ],
    IssueCategory.CUSTOMER_LOCATION_DIFFICULTY: [
        SubIssue("Customer location finding assistance", "handle_navigation_location", "Delivery agent navigation support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.navigation_location_handler")
    ],
    
    # Logistics Issues
    IssueCategory.TRAFFIC_DELAYS: [
        SubIssue("Traffic delay management", "handle_logistics", "Delivery agent traffic delay support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.logistics_handler")
    ],
    IssueCategory.VEHICLE_BREAKDOWN: [
        SubIssue("Vehicle breakdown assistance", "handle_logistics", "Delivery agent vehicle emergency support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.logistics_handler")
    ],
    IssueCategory.SAFETY_ACCIDENT_ENROUTE: [
        SubIssue("Safety and accident support", "handle_logistics", "Delivery agent emergency safety assistance", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.logistics_handler")
    ],
    IssueCategory.ORDER_BATCHING_CONFUSION: [
        SubIssue("Order batching confusion resolution", "handle_logistics", "Delivery agent multi-order management support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.logistics_handler")
    ],
    
    # Operational Issues
    IssueCategory.PACKAGE_TAMPERED_SPILLED: [
        SubIssue("Package tampering and spillage handling", "handle_operational", "Delivery agent package integrity support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.operational_handler")
    ],
    IssueCategory.WRONG_PACKAGE_HANDOVER: [
        SubIssue("Wrong package delivery resolution", "handle_operational", "Delivery agent package verification support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.operational_handler")
    ],
    IssueCategory.PAYMENT_COLLECTION_COD: [
        SubIssue("Payment collection COD support", "handle_operational", "Delivery agent payment processing assistance", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.operational_handler")
    ],
    IssueCategory.CUSTOMER_UNAVAILABLE_DELIVERY: [
        SubIssue("Customer unavailability management", "handle_operational", "Delivery agent customer contact support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.operational_handler")
    ],
    IssueCategory.LONG_WAIT_CUSTOMER_LOCATION: [
        SubIssue("Customer location wait time management", "handle_operational", "Delivery agent waiting time support", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.operational_handler")
    ],
    IssueCategory.CUSTOMER_LATE_CANCELLATION: [
        SubIssue("Late customer cancellation support", "handle_operational", "Delivery agent cancellation compensation", GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT, "grab_food.delivery_agent.operational_handler")
    ],
}

# Actor-based issue mappings for Grab Mart Customer
GRAB_MART_CUSTOMER_ISSUES = {
    # Order Accuracy & Quality Issues
    IssueCategory.ITEMS_MISSING: [
        SubIssue("Missing items in delivery", "handle_missing_items", "Customer missing items resolution", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.order_quality_handler")
    ],
    IssueCategory.POOR_QUALITY: [
        SubIssue("Wrong item delivered", "handle_wrong_item", "Customer wrong item resolution", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.order_quality_handler"),
        SubIssue("Expired/damaged/poor quality items", "handle_quality_issues", "Customer quality guarantee", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.order_quality_handler"),
    ],
    IssueCategory.PORTION_INADEQUATE: [
        SubIssue("Substituted item not acceptable", "handle_substitution_issues", "Customer substitution preference", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.order_quality_handler"),
        SubIssue("Quantity mismatch", "handle_quantity_mismatch", "Customer quantity accuracy", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.order_quality_handler")
    ],
    
    # Delivery Experience Issues  
    IssueCategory.ORDER_NOT_RECEIVED: [
        SubIssue("Delay beyond promised time", "handle_delivery_delay", "Customer delivery delay compensation", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.delivery_experience_handler"),
        SubIssue("Partial order delivered", "handle_partial_delivery", "Customer partial order resolution", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.delivery_experience_handler"),
    ],
    IssueCategory.SPILLAGE: [
        SubIssue("Cold/frozen items melted or leaked", "handle_temperature_issues", "Customer temperature control guarantee", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.delivery_experience_handler"),
        SubIssue("Package tampered or unsealed", "handle_package_tampering", "Customer package security guarantee", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.delivery_experience_handler"),
    ],
    IssueCategory.ROUTING_TRACKING_ISSUES: [
        SubIssue("Multiple deliveries for same order", "handle_multiple_deliveries", "Customer delivery consolidation", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.delivery_experience_handler")
    ],
    
    # Driver Interaction Issues
    IssueCategory.DRIVER_BEHAVIOR: [
        SubIssue("Rude behavior from delivery partner", "handle_rude_behavior", "Customer professional service standards", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.driver_interaction_handler"),
        SubIssue("Driver unable to find address, keeps calling", "handle_location_difficulty", "Customer navigation assistance", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.driver_interaction_handler"),
    ],
    IssueCategory.FRAUD: [
        SubIssue("Driver asks for extra money (COD manipulation)", "handle_payment_manipulation", "Customer payment protection", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.driver_interaction_handler"),
        SubIssue("Driver marks delivered but no package received", "handle_false_delivery", "Customer delivery verification", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.driver_interaction_handler"),
    ],
    
    # Payment & Refund Issues
    IssueCategory.PAYMENT_BILLING: [
        SubIssue("Double charge for single order", "handle_double_charge", "Customer billing error resolution", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.payment_refund_handler"),
        SubIssue("Failed payment but money deducted", "handle_failed_payment_money_deducted", "Customer payment error resolution", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.payment_refund_handler"),
        SubIssue("COD order marked prepaid", "handle_cod_marked_prepaid", "Customer payment method correction", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.payment_refund_handler"),
        SubIssue("Refund not initiated for missing/damaged items", "handle_refund_not_initiated", "Customer refund processing", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.payment_refund_handler"),
    ],
    
    # Technical Issues
    IssueCategory.COUPON_QUERY: [
        SubIssue("Order auto-cancelled without reason", "handle_auto_cancellation", "Customer system error resolution", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.technical_handler"),
        SubIssue("App shows delivered but not received", "handle_delivery_status_error", "Customer delivery status correction", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.technical_handler"),
        SubIssue("Wrong tracking status", "handle_tracking_status_error", "Customer tracking accuracy", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.technical_handler"),
        SubIssue("Coupons/offers not applied correctly", "handle_coupon_offers_error", "Customer promotional savings", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.technical_handler"),
    ],
    
    # Original Grab Mart specific issues
    IssueCategory.PRODUCT_QUALITY: [
        SubIssue("Customer freshness concerns", "handle_customer_grocery_freshness", "Customer freshness guarantee", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.shopping_experience_handler"),
        SubIssue("Customer bulk shopping", "handle_customer_bulk_shopping", "Customer bulk shopping excellence", GrabService.GRAB_MART, Actor.CUSTOMER, "grab_mart.customer.shopping_experience_handler"),
    ],
}

# Actor-based issue mappings for Grab Mart Dark House
GRAB_MART_DARK_HOUSE_ISSUES = {
    IssueCategory.ITEMS_MISSING: [
        SubIssue("Inventory shortage management", "handle_inventory_shortage", "Dark house inventory management", GrabService.GRAB_MART, Actor.DARK_HOUSE, "grab_mart.dark_house.inventory_handler")
    ],
    IssueCategory.POOR_QUALITY: [
        SubIssue("Product quality control", "handle_product_quality_control", "Dark house quality control", GrabService.GRAB_MART, Actor.DARK_HOUSE, "grab_mart.dark_house.inventory_handler"),
        SubIssue("Picking accuracy improvement", "handle_picking_accuracy", "Dark house picking accuracy", GrabService.GRAB_MART, Actor.DARK_HOUSE, "grab_mart.dark_house.inventory_handler"),
    ],
    IssueCategory.PRODUCT_QUALITY: [
        SubIssue("Warehouse efficiency optimization", "handle_warehouse_efficiency", "Dark house operational efficiency", GrabService.GRAB_MART, Actor.DARK_HOUSE, "grab_mart.dark_house.inventory_handler"),
        SubIssue("Temperature control management", "handle_temperature_control", "Dark house cold chain management", GrabService.GRAB_MART, Actor.DARK_HOUSE, "grab_mart.dark_house.inventory_handler"),
    ],
}

# Actor-based issue mappings for Grab Mart Delivery Agent  
GRAB_MART_DELIVERY_ISSUES = {
    # Technical Issues
    IssueCategory.ORDER_NOT_RECEIVED: [
        SubIssue("Delivery time performance", "handle_technical", "Delivery agent time optimization", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.technical_handler"),
        SubIssue("Delivery accuracy issues", "handle_technical", "Delivery agent accuracy improvement", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.technical_handler"),
    ],
    IssueCategory.POOR_QUALITY: [
        SubIssue("Delivery communication", "handle_technical", "Delivery agent communication excellence", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.technical_handler"),
        SubIssue("Delivery safety protocols", "handle_technical", "Delivery agent safety compliance", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.technical_handler"),
        SubIssue("Delivery equipment maintenance", "handle_technical", "Delivery agent equipment standards", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.technical_handler"),
    ],
    # Navigation & Location Issues
    IssueCategory.INCORRECT_CUSTOMER_ADDRESS: [
        SubIssue("Incorrect customer address resolution", "handle_navigation_location", "Delivery agent address verification support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.navigation_location_handler")
    ],
    IssueCategory.GPS_APP_TECHNICAL_ISSUES: [
        SubIssue("GPS and app technical support", "handle_navigation_location", "Delivery agent GPS technical issue resolution", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.navigation_location_handler")
    ],
    IssueCategory.CUSTOMER_LOCATION_DIFFICULTY: [
        SubIssue("Customer location finding assistance", "handle_navigation_location", "Delivery agent navigation support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.navigation_location_handler")
    ],
    
    # Logistics Issues
    IssueCategory.TRAFFIC_DELAYS: [
        SubIssue("Traffic delay management", "handle_logistics", "Delivery agent traffic delay support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.logistics_handler")
    ],
    IssueCategory.VEHICLE_BREAKDOWN: [
        SubIssue("Vehicle breakdown assistance", "handle_logistics", "Delivery agent vehicle emergency support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.logistics_handler")
    ],
    IssueCategory.SAFETY_ACCIDENT_ENROUTE: [
        SubIssue("Safety and accident support", "handle_logistics", "Delivery agent emergency safety assistance", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.logistics_handler")
    ],
    IssueCategory.ORDER_BATCHING_CONFUSION: [
        SubIssue("Order batching confusion resolution", "handle_logistics", "Delivery agent multi-order management support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.logistics_handler")
    ],
    
    # Operational Issues
    IssueCategory.PACKAGE_TAMPERED_SPILLED: [
        SubIssue("Package tampering and spillage handling", "handle_operational", "Delivery agent package integrity support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.operational_handler")
    ],
    IssueCategory.WRONG_PACKAGE_HANDOVER: [
        SubIssue("Wrong package delivery resolution", "handle_operational", "Delivery agent package verification support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.operational_handler")
    ],
    IssueCategory.PAYMENT_COLLECTION_COD: [
        SubIssue("Payment collection COD support", "handle_operational", "Delivery agent payment processing assistance", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.operational_handler")
    ],
    IssueCategory.CUSTOMER_UNAVAILABLE_DELIVERY: [
        SubIssue("Customer unavailability management", "handle_operational", "Delivery agent customer contact support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.operational_handler")
    ],
    IssueCategory.LONG_WAIT_CUSTOMER_LOCATION: [
        SubIssue("Customer location wait time management", "handle_operational", "Delivery agent waiting time support", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.operational_handler")
    ],
    IssueCategory.CUSTOMER_LATE_CANCELLATION: [
        SubIssue("Late customer cancellation support", "handle_operational", "Delivery agent cancellation compensation", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.operational_handler")
    ],
    
    # Original Grab Mart specific delivery issues
    IssueCategory.PRODUCT_QUALITY: [
        SubIssue("Grocery handling standards", "handle_grocery_handling_standards", "Grocery delivery handling excellence", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.grocery_delivery_handler"),
        SubIssue("Cold chain delivery", "handle_cold_chain_delivery", "Grocery cold chain delivery protocol", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.grocery_delivery_handler"),
        SubIssue("Customer communication grocery", "handle_customer_communication_grocery", "Grocery delivery communication excellence", GrabService.GRAB_MART, Actor.DELIVERY_AGENT, "grab_mart.delivery_agent.grocery_delivery_handler"),
    ],
}

# Actor-based issue mappings for Grab Cabs Customer
GRAB_CABS_CUSTOMER_ISSUES = {
    IssueCategory.RIDE_ISSUES: [
        SubIssue("Customer ride safety", "handle_customer_ride_safety", "Customer ride safety priority", GrabService.GRAB_CABS, Actor.CUSTOMER, "grab_cabs.customer.ride_experience_handler"),
        SubIssue("Customer ride comfort", "handle_customer_ride_comfort", "Customer ride comfort guarantee", GrabService.GRAB_CABS, Actor.CUSTOMER, "grab_cabs.customer.ride_experience_handler"),
    ],
    IssueCategory.DRIVER_BEHAVIOR: [
        SubIssue("Customer driver behavior", "handle_customer_driver_behavior", "Customer professional service standards", GrabService.GRAB_CABS, Actor.CUSTOMER, "grab_cabs.customer.ride_experience_handler"),
        SubIssue("Customer booking issues", "handle_customer_booking_issues", "Customer booking support", GrabService.GRAB_CABS, Actor.CUSTOMER, "grab_cabs.customer.ride_experience_handler"),
    ],
    IssueCategory.PAYMENT_BILLING: [
        SubIssue("Customer payment dispute", "handle_customer_payment_dispute", "Customer payment resolution", GrabService.GRAB_CABS, Actor.CUSTOMER, "grab_cabs.customer.ride_experience_handler")
    ],
}

# Actor-based issue mappings for Grab Express Customer
GRAB_EXPRESS_CUSTOMER_ISSUES = {
    # Order Accuracy & Quality Issues
    IssueCategory.ITEMS_MISSING: [
        SubIssue("Missing package in delivery", "handle_missing_items", "Customer missing package resolution", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.order_quality_handler")
    ],
    IssueCategory.POOR_QUALITY: [
        SubIssue("Wrong package delivered", "handle_wrong_item", "Customer wrong package resolution", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.order_quality_handler"),
        SubIssue("Damaged package during transit", "handle_quality_issues", "Customer package protection guarantee", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.order_quality_handler"),
    ],
    IssueCategory.PORTION_INADEQUATE: [
        SubIssue("Package contents incomplete", "handle_substitution_issues", "Customer package completeness verification", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.order_quality_handler"),
        SubIssue("Package size mismatch", "handle_quantity_mismatch", "Customer package size accuracy", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.order_quality_handler")
    ],
    
    # Delivery Experience Issues  
    IssueCategory.ORDER_NOT_RECEIVED: [
        SubIssue("Delay beyond promised time", "handle_delivery_delay", "Customer express delivery guarantee", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.delivery_experience_handler"),
        SubIssue("Package not delivered to correct recipient", "handle_partial_delivery", "Customer delivery verification", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.delivery_experience_handler"),
    ],
    IssueCategory.SPILLAGE: [
        SubIssue("Package damaged or opened during transit", "handle_temperature_issues", "Customer package integrity guarantee", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.delivery_experience_handler"),
        SubIssue("Package tampered or unsealed", "handle_package_tampering", "Customer package security guarantee", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.delivery_experience_handler"),
    ],
    IssueCategory.ROUTING_TRACKING_ISSUES: [
        SubIssue("Multiple delivery attempts for same package", "handle_multiple_deliveries", "Customer delivery consolidation", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.delivery_experience_handler")
    ],
    
    # Driver Interaction Issues
    IssueCategory.DRIVER_BEHAVIOR: [
        SubIssue("Rude behavior from delivery partner", "handle_rude_behavior", "Customer professional service standards", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.driver_interaction_handler"),
        SubIssue("Delivery partner unable to find address", "handle_location_difficulty", "Customer navigation assistance", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.driver_interaction_handler"),
    ],
    IssueCategory.FRAUD: [
        SubIssue("Delivery partner asks for extra money", "handle_payment_manipulation", "Customer payment protection", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.driver_interaction_handler"),
        SubIssue("Delivery partner marks delivered but no package received", "handle_false_delivery", "Customer delivery verification", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.driver_interaction_handler"),
    ],
    
    # Payment & Refund Issues
    IssueCategory.PAYMENT_BILLING: [
        SubIssue("Double charge for single delivery", "handle_double_charge", "Customer billing error resolution", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.payment_refund_handler"),
        SubIssue("Failed payment but money deducted", "handle_failed_payment_money_deducted", "Customer payment error resolution", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.payment_refund_handler"),
        SubIssue("COD delivery marked prepaid", "handle_cod_marked_prepaid", "Customer payment method correction", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.payment_refund_handler"),
        SubIssue("Refund not initiated for damaged/lost package", "handle_refund_not_initiated", "Customer refund processing", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.payment_refund_handler"),
    ],
    
    # Technical Issues
    IssueCategory.COUPON_QUERY: [
        SubIssue("Delivery auto-cancelled without reason", "handle_auto_cancellation", "Customer system error resolution", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.technical_handler"),
        SubIssue("App shows delivered but not received", "handle_delivery_status_error", "Customer delivery status correction", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.technical_handler"),
        SubIssue("Wrong tracking status", "handle_tracking_status_error", "Customer tracking accuracy", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.technical_handler"),
        SubIssue("Coupons/offers not applied correctly", "handle_coupon_offers_error", "Customer promotional savings", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.technical_handler"),
    ],
    
    # Grab Express specific issues with vehicle type information
    IssueCategory.PACKAGE_SIZE_VEHICLE_MISMATCH: [
        SubIssue("Package too large for bike delivery", "handle_vehicle_size_mismatch", "Customer vehicle type optimization - Bike delivery limitations", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.vehicle_matching_handler"),
        SubIssue("Package requires truck but bike assigned", "handle_vehicle_upgrade_needed", "Customer vehicle type upgrade - Truck delivery required", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.vehicle_matching_handler"),
        SubIssue("Heavy package assigned to standard car", "handle_weight_vehicle_mismatch", "Customer vehicle capacity matching - Car to truck upgrade", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.vehicle_matching_handler"),
    ],
    IssueCategory.EXPRESS_DELIVERY_URGENCY: [
        SubIssue("Same day delivery not available for bike", "handle_urgency_vehicle_conflict", "Customer express delivery vehicle limitation - Bike capacity", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.express_service_handler"),
        SubIssue("Urgent delivery requires faster vehicle type", "handle_speed_requirements", "Customer express delivery optimization - Vehicle speed matching", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.express_service_handler"),
    ],
    IssueCategory.VEHICLE_TYPE_REQUIREMENTS: [
        SubIssue("Fragile items need car instead of bike", "handle_fragile_vehicle_requirements", "Customer fragile package protection - Car delivery required", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.special_handling_handler"),
        SubIssue("Temperature sensitive delivery needs refrigerated truck", "handle_temperature_vehicle_requirements", "Customer temperature control - Refrigerated truck delivery", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.special_handling_handler"),
        SubIssue("Bulk delivery requires truck capacity", "handle_bulk_delivery_requirements", "Customer bulk package handling - Truck delivery capacity", GrabService.GRAB_EXPRESS, Actor.CUSTOMER, "grab_express.customer.special_handling_handler"),
    ],
}

# Actor-based issue mappings for Grab Cabs Driver
GRAB_CABS_DRIVER_ISSUES = {
    IssueCategory.DRIVER_BEHAVIOR: [
        SubIssue("Driver cancellation penalty", "handle_driver_cancellation_penalty", "Driver performance accountability", GrabService.GRAB_CABS, Actor.DRIVER, "grab_cabs.driver.performance_handler"),
        SubIssue("Driver behavior coaching", "handle_driver_behavior_coaching", "Driver professional behavior training", GrabService.GRAB_CABS, Actor.DRIVER, "grab_cabs.driver.performance_handler"),
    ],
    IssueCategory.RIDE_ISSUES: [
        SubIssue("Driver route training", "handle_driver_route_training", "Driver route optimization training", GrabService.GRAB_CABS, Actor.DRIVER, "grab_cabs.driver.performance_handler"),
        SubIssue("Driver vehicle standards", "handle_driver_vehicle_standards", "Driver vehicle maintenance standards", GrabService.GRAB_CABS, Actor.DRIVER, "grab_cabs.driver.performance_handler"),
    ],
    IssueCategory.PAYMENT_BILLING: [
        SubIssue("Driver earnings impact", "handle_driver_earnings_impact", "Driver earnings recovery plan", GrabService.GRAB_CABS, Actor.DRIVER, "grab_cabs.driver.performance_handler")
    ],
}

# Combined actor-based mapping for all services and actors
ACTOR_ISSUE_MAPPING = {
    # Grab Food actor mappings
    (GrabService.GRAB_FOOD, Actor.CUSTOMER): GRAB_FOOD_ISSUES,
    (GrabService.GRAB_FOOD, Actor.RESTAURANT): GRAB_FOOD_RESTAURANT_ISSUES,
    (GrabService.GRAB_FOOD, Actor.DELIVERY_AGENT): GRAB_FOOD_DELIVERY_ISSUES,
    
    # Grab Mart actor mappings
    (GrabService.GRAB_MART, Actor.CUSTOMER): GRAB_MART_CUSTOMER_ISSUES,
    (GrabService.GRAB_MART, Actor.DARK_HOUSE): GRAB_MART_DARK_HOUSE_ISSUES,
    (GrabService.GRAB_MART, Actor.DELIVERY_AGENT): GRAB_MART_DELIVERY_ISSUES,
    
    # Grab Cabs actor mappings
    (GrabService.GRAB_CABS, Actor.CUSTOMER): GRAB_CABS_CUSTOMER_ISSUES,
    (GrabService.GRAB_CABS, Actor.DRIVER): GRAB_CABS_DRIVER_ISSUES,
    
    # Grab Express actor mappings
    (GrabService.GRAB_EXPRESS, Actor.CUSTOMER): GRAB_EXPRESS_CUSTOMER_ISSUES,
}

# Backwards compatibility - combined service mapping
ISSUE_MAPPING = {
    GrabService.GRAB_FOOD: GRAB_FOOD_ISSUES,
    GrabService.GRAB_MART: GRAB_MART_CUSTOMER_ISSUES,  # Default to customer view
    GrabService.GRAB_CABS: GRAB_CABS_CUSTOMER_ISSUES,  # Default to customer view
    GrabService.GRAB_EXPRESS: GRAB_EXPRESS_CUSTOMER_ISSUES,  # Default to customer view
}

# Actor mapping for each service
SERVICE_ACTORS = {
    GrabService.GRAB_FOOD: [Actor.CUSTOMER, Actor.RESTAURANT, Actor.DELIVERY_AGENT],
    GrabService.GRAB_MART: [Actor.CUSTOMER, Actor.DARK_HOUSE, Actor.DELIVERY_AGENT],
    GrabService.GRAB_CABS: [Actor.CUSTOMER, Actor.DRIVER],
    GrabService.GRAB_EXPRESS: [Actor.CUSTOMER, Actor.EXPRESS_DELIVERY_PARTNER],
}
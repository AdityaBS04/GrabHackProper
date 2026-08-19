# GrabHack — AI-Powered Customer Service Platform

## What This Is

GrabHack is a hackathon prototype of an **AI-driven customer service chatbot** built for Grab's ecosystem. It supports four Grab services (GrabFood, GrabMart, GrabCabs, GrabExpress) and handles complaints from every type of actor in the system — customers, delivery agents, restaurants, cab drivers, and dark-store warehouse staff.

The key idea: instead of a single generic chatbot, the system routes each complaint to a specialized handler that knows exactly what issue is being raised, what the user's order history looks like, and whether photo evidence is needed.

---

## High-Level Architecture

```
Browser (React SPA)
    │
    │  HTTP / JSON
    ▼
Flask REST API  (GrabHack/app.py)  ←──  SQLite DB (grabhack.db)
    │
    ├── Service Handlers (modular Python files per service/actor)
    │       grab_food/customer, grab_food/delivery_agent, ...
    │
    ├── Enhanced AI Engine (enhanced_ai_engine_fixed.py)
    │       Groq API  →  text model, image model, security model
    │       Google Maps API  →  navigation links
    │
    └── Cross-Actor Update Service (cross_actor_service.py)
            Real-time notifications between actors
```

Deployment is via Docker Compose: `backend` on port 8000, `frontend` on port 3000.

---

## Database Schema

Five tables in `grabhack.db`:

| Table | Purpose |
|---|---|
| `users` | Login credentials + `credibility_score` (1–10) |
| `orders` | All orders across all services; includes GPS coordinates, order items, payment method, update tracking fields |
| `complaints` | Each complaint filed, with AI-generated solution stored back |
| `order_updates` | Audit log of every cross-actor status change |
| `actor_notifications` | Push notifications generated for each affected actor when an update occurs |

---

## Data Model (models.py)

**GrabService** — the four services:
`grab_food`, `grab_mart`, `grab_cabs`, `grab_express`

**Actor** — who is using the system:
`customer`, `delivery_agent`, `restaurant`, `driver`, `dark_house`, `express_delivery_partner`

**IssueCategory** — 39 named complaint categories (e.g. `ITEMS_MISSING`, `FRAUD`, `GPS_APP_TECHNICAL_ISSUES`, `PACKAGE_SIZE_VEHICLE_MISMATCH`, …)

**SubIssue** — the atomic unit: ties together a human-readable name, a Python function name (`tool_name`), and the exact handler module path. For example:

```
SubIssue(
    name="Missing items in delivery",
    tool_name="handle_missing_items",
    handler_module="grab_food.customer.order_quality_handler"
)
```

**ACTOR_ISSUE_MAPPING** — a dict keyed by `(GrabService, Actor)` that maps each issue category to its list of sub-issues. This is what the API uses to populate the chatbot's category and sub-issue menus.

---

## Service Handler Tree

Every leaf in this tree is a Python file with a Handler class that has methods named `handle_<something>`:

```
GrabHack/
├── grab_food/
│   ├── customer/
│   │   ├── order_quality_handler.py        (missing items, wrong item, quality, substitution)
│   │   ├── delivery_experience_handler.py  (delays, partial delivery, spillage, tampering)
│   │   ├── driver_interaction_handler.py   (rude behavior, false delivery, COD fraud)
│   │   ├── payment_refund_handler.py       (double charge, failed payment, refunds)
│   │   └── technical_handler.py            (auto-cancel, tracking errors, coupon bugs)
│   ├── delivery_agent/
│   │   ├── navigation_location_handler.py  (wrong address, GPS issues, finding customers)
│   │   ├── logistics_handler.py            (traffic, vehicle breakdown, safety incidents)
│   │   ├── operational_handler.py          (wrong package, COD collection, late cancellations)
│   │   └── technical_handler.py            (performance, communication issues)
│   └── restaurant/
│       └── restaurant_handler.py           (food safety, prep delays, delivery partner shortage)
│
├── grab_mart/
│   ├── customer/                           (mirrors grab_food customer + shopping_experience_handler)
│   ├── delivery_agent/                     (mirrors grab_food delivery_agent + grocery_delivery_handler)
│   └── dark_house/
│       ├── inventory_handler.py            (stock shortages, quality control, picking accuracy)
│       └── dark_store_handler.py
│
├── grab_cabs/
│   ├── customer/
│   │   ├── customer_experience.py          (harassment, app/booking issues, cancellation/refund, airport problems)
│   │   ├── driver_vehicle_issues.py        (unsafe driving, vehicle condition, accidents)
│   │   ├── fare_payment.py
│   │   └── operational_issues.py / operational_problems.py
│   └── driver/
│       ├── customer_experience.py          (passenger harassment, false complaints)
│       ├── driver_vehicle_issues.py        (breakdown, passenger damage, insurance)
│       ├── fare_payment.py                 (incorrect fare, payout delays, commission)
│       ├── operational_issues.py           (cancellations after arrival, wrong details)
│       └── operational_problems.py         (no rides, unfair allocation, navigation)
│
└── grab_express/
    └── customer/
        ├── order_quality_handler.py
        ├── delivery_experience_handler.py
        ├── driver_interaction_handler.py
        ├── payment_refund_handler.py
        ├── technical_handler.py
        ├── vehicle_matching_handler.py     (package too large for bike, truck upgrades)
        ├── express_service_handler.py      (urgent delivery, speed requirements)
        └── special_handling_handler.py     (fragile items, refrigerated truck, bulk)
```

---

## AI Engine (enhanced_ai_engine_fixed.py)

The `EnhancedAgenticAIEngine` class orchestrates four different AI models via the Groq API:

| Model | Role |
|---|---|
| `openai/gpt-oss-120b` | Text-only complaint resolution |
| `meta-llama/llama-4-maverick-17b-128e-instruct` | Image analysis (food photos, vehicle damage, etc.) |
| `meta-llama/llama-prompt-guard-2-86m` | Security screening — blocks inappropriate image uploads |
| `llama-3.3-70b-versatile` | Conversation orchestration and fraud detection |

### Complaint Processing Pipeline

```
process_complaint()
    1. Order status check — if order is still in_progress, block quality complaints
    2. Image security screening — Prompt Guard model flags unsafe uploads
    3. Check image_required_functions dict — does this issue need a photo?
    4. If image required and not provided → ask user to upload
    5. If image present → image model (fraud-detection conversation)
    6. If text only → text model (6-sentence resolution)
```

### Conversation Processing Pipeline (`process_conversation`)

Used by the `/api/chat` endpoint for multi-turn conversations:

1. Check order status (same gate as above)
2. If a sub-issue is already selected: send order history + conversation history to orchestrator model, which responds with JSON `{response_text, needs_image, escalate_to_human}`
3. If no sub-issue yet: orchestrator model analyzes the free-text message to identify the issue type and decide whether an image is needed

### Google Maps Integration

Navigation issues (GPS crashes, wrong addresses) skip the LLM and instead generate direct Google Maps and Waze links using the real coordinates stored in the orders table. If a Google Maps API key is set, it also returns live distance and ETA.

---

## Backend API Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/api/login` | Authenticate user; returns user type, credibility score, accessible services |
| GET | `/api/orders/<user_type>/<username>` | Fetch all orders for a user |
| GET | `/api/orders/<user_type>/<username>/with-updates` | Same, but includes unread notification count per order |
| GET | `/api/categories/<service>/<user_type>` | Get top-level complaint categories for the chatbot menu |
| GET | `/api/subissues/<service>/<user_type>/<category_id>` | Get sub-issues for a chosen category |
| POST | `/api/complaint` | Submit a complaint; calls AI engine; stores solution |
| POST | `/api/missing-items` | Dedicated endpoint that generates an interactive item checklist from the actual order |
| POST | `/api/chat` | Multi-turn chat message; routes to correct handler or AI engine |
| POST | `/api/chat/image` | Upload an image mid-conversation; hands off to image model |
| POST | `/api/order-update` | Actor posts a cross-actor update (e.g. restaurant adds dish) |
| GET | `/api/notifications/<actor_type>/<username>` | Fetch notifications for an actor |
| PUT | `/api/notifications/<id>/read` | Mark a notification as read |
| GET | `/api/order-history/<order_id>` | Get the full update timeline for one order |

---

## Cross-Actor Update System (cross_actor_service.py)

When one actor in the system does something that affects others, a cross-actor update is created. The system automatically figures out who needs to be notified and sends them a message.

**Example update types and who they notify:**

| Update Type | Triggered By | Notifies |
|---|---|---|
| `dish_added` | Restaurant | Customer |
| `preparation_delayed` | Restaurant | Customer + Delivery Agent |
| `route_changed` | Driver | Customer + Restaurant |
| `delivery_delayed` | Driver | Customer + Restaurant |
| `address_updated` | Customer | Delivery Agent + Restaurant |
| `item_substituted` | Dark Store | Customer + Delivery Agent |
| `vehicle_upgraded` | System | Customer |

**Spam prevention:** max 5 updates per order per hour, max 10 updates per actor per hour, duplicate updates within 10 minutes are rejected.

---

## Frontend (React SPA)

Three pages, accessible at these routes:

### `/login` — Login Page
- Animated background with GrabHack branding
- Username + password form (calls `/api/login`)
- Saves user object (type, username, credibility score, accessible services) to `localStorage`
- Redirects to `/dashboard`

### `/dashboard` — Dashboard
- Shows the logged-in user's orders (fetched from `/api/orders/...with-updates`)
- Displays a **NotificationCenter** for unread cross-actor messages
- Each order card has a "View Timeline" button that opens the **OrderTimeline** component (fetches from `/api/order-history/<order_id>`)
- A "Report Issue" button navigates to `/complaint` passing `service` and `orderId` as route state

### `/complaint` — ChatBot
Three-phase conversation flow:

1. **Category selection** — bot displays chips for the top-level categories (fetched from `/api/categories`)
2. **Sub-issue selection** — after a category is chosen, bot shows specific sub-issues (fetched from `/api/subissues`)
3. **Free-text conversation** — messages go to `/api/chat`; responses may include an image upload prompt, which sends to `/api/chat/image`

The ChatBot formats LLM output (markdown-style bold, bullet points) and shows a typing indicator while waiting for responses.

---

## Demo Users

All passwords are `pass123`. User types determine which services and complaint categories they see.

| Username | Type | Credibility |
|---|---|---|
| `customer1` | customer | 9 (high — loyal) |
| `customer2` | customer | 5 (medium — some issues) |
| `customer3` | customer | 3 (low — frequent complaints) |
| `john_doe` | customer | 8 |
| `jane_smith` | customer | 7 |
| `test_user` | customer | 4 |
| `agent1/2/3`, `fast_rider` | delivery_agent | 7–9 |
| `resto1/2/3`, `pizza_palace`, `burger_joint` | restaurant | 6–9 |
| `driver1/2/3` | driver | 6–8 |
| `store1/2` | darkstore | 7–8 |

The credibility score is passed to the AI as context so the model can tailor its response — a user with score 3 who claims a missing item receives more scrutiny than one with score 9.

---

## Key Smart Behaviors

### Order-Status Gating
If a customer tries to file a food-quality or missing-items complaint while their order is still `in_progress`, `preparing`, `assigned`, or `picking`, the system blocks it and asks them to wait until delivery is complete.

### Image-Required Complaints
Many complaint types (missing items, wrong item, vehicle damage, driver harassment, food quality, package tampering) require a photo before the AI will process the complaint. If no image is provided, the system responds with an upload prompt instead of a resolution.

### Fraud Detection
When an image is uploaded, the image model describes what it sees and cross-references it against the customer's actual order data (items ordered, restaurant, price). If something doesn't match up, it asks follow-up questions or escalates to a human agent.

### Personalized Responses
Every AI response is generated with the customer's last 10 orders included as context. The model references specific order IDs, restaurant names, and items — making the interaction feel personalized rather than generic.

### Interactive Missing-Items Selection
For GrabFood missing items, instead of asking the user to describe what's missing, the system fetches their actual order's food items from the database and presents a numbered checklist (`☐ 1. Margherita Pizza`, `☐ 2. Garlic Bread`, …) so they can pick exactly which items didn't arrive.

---

## Environment Variables Required

| Variable | Used For |
|---|---|
| `GROQ_API_KEY` | All AI model calls |
| `GOOGLE_MAPS_API_KEY` | Navigation geocoding and direction links (optional; falls back to URL-based links) |

---

## How to Run

```bash
# With Docker Compose (recommended)
docker-compose up

# Or manually
cd GrabHack
pip install -r requirements.txt
python app.py          # starts on port 8000

cd ../frontend
npm install
npm start              # starts on port 3000
```

The database is auto-initialized with demo users and sample orders on first run.

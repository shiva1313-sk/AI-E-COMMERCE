import re
from typing import Any, Dict, List, Optional


class OrderService:
    """Ground-truth order status resolver that checks real application order data."""

    def resolve_order_query(self, query: str, orders: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Resolve order-related questions strictly from provided order data:
        1. If no order data is available -> return grounded fallback.
        2. If specific Order ID is referenced -> lookup exact order.
        3. If product name/type is referenced in query -> lookup matching order item.
        4. If 1 order exists -> return actual status and delivery timeline.
        5. If multiple orders exist and query is ambiguous -> ask short clarification.
        """
        clean_query = query.strip()
        lower_query = clean_query.lower()

        if not orders or len(orders) == 0:
            return "I couldn't find order information for this request."

        # 1. Check for specific Order ID in query (e.g. OD1024, #OD1234567890, ORD1024)
        id_match = re.search(r'\b(?:#|order\s+)?(OD\d+|ORD\d+|\d{6,12})\b', clean_query, re.I)
        if id_match:
            target_id = id_match.group(1).upper()
            matched_order = next((o for o in orders if str(o.get("orderId", "")).upper() == target_id or target_id in str(o.get("orderId", "")).upper()), None)
            if matched_order:
                return self._format_single_order(matched_order)
            else:
                return f"I couldn't find an order matching #{target_id} in your account."

        # 2. Check if query references a specific product category or keyword (e.g. "laptop", "shoes", "phone")
        matched_by_product = []
        for o in orders:
            items = o.get("items", [])
            for item in items:
                prod = item.get("product", {})
                p_name = prod.get("name", "").lower()
                p_cat = prod.get("category", "").lower()
                
                # Check keywords in query
                for kw in ["laptop", "phone", "smartphone", "shoes", "shoe", "headphones", "earbuds", "watch", "keyboard", "mouse", "backpack"]:
                    if kw in lower_query and (kw in p_name or kw in p_cat):
                        matched_by_product.append(o)
                        break

        if len(matched_by_product) == 1:
            return self._format_single_order(matched_by_product[0])
        elif len(matched_by_product) > 1:
            return f"I found {len(matched_by_product)} orders matching your query. Which order ID would you like to check?"

        # 3. Single order handling
        if len(orders) == 1:
            return self._format_single_order(orders[0])

        # 4. Multiple orders and ambiguous query
        return f"I found {len(orders)} recent orders in your account. Which product or order ID would you like to check?"

    def _format_single_order(self, order: Dict[str, Any]) -> str:
        """Format a single order status into 1-2 concise grounded sentences."""
        order_id = order.get("orderId", "Order")
        status = order.get("status", "Processing")
        expected = order.get("expectedDelivery", "Soon")
        
        items = order.get("items", [])
        item_names = []
        for item in items:
            prod = item.get("product", {})
            name = prod.get("name")
            if name:
                item_names.append(name)

        item_str = ", ".join(item_names[:2]) if item_names else "your items"
        if len(item_names) > 2:
            item_str += f" (+{len(item_names) - 2} more)"

        return f"Your order #{order_id} for {item_str} is currently {status}, with expected delivery {expected}."


order_service = OrderService()

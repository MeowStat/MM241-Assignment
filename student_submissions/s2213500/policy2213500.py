from policy import Policy

class Policy2213500(Policy):
    def __init__(self):
        pass

    def get_action(self, observation, info):
        list_prods = observation["products"]
        stock_idx = -1
        pos_x, pos_y = 0, 0

        # Sort products by size for better table management
        sorted_prods = sorted(list_prods, key=lambda prod: prod["size"][0] * prod["size"][1], reverse=True)

        # DP Table to store best fit solutions for products
        dp = {}

        # Helper function to compute the maximum remaining space for a given stock
        def max_remaining_space(stock, product_size):
            stock_w, stock_h = self._get_stock_size_(stock)
            prod_w, prod_h = product_size

            if stock_w < prod_w or stock_h < prod_h:
                return None  # Product doesn't fit in the stock

            # Let's assume we only calculate the best fitting positions for the product
            best_remaining_space = stock_w * stock_h - (prod_w * prod_h)  # Simplified assumption (can be improved)
            return best_remaining_space

        # Try placing the products in the most efficient stock configuration using DP
        def dp_solver(stock_idx, remaining_space, prod_size):
            if (stock_idx, remaining_space) in dp:
                return dp[(stock_idx, remaining_space)]

            # Base case: No remaining space, placement impossible
            if remaining_space < 0:
                return None

            best_position = None
            stock = observation["stocks"][stock_idx]
            stock_w, stock_h = self._get_stock_size_(stock)
            prod_w, prod_h = prod_size

            # Try all possible positions in the stock
            for x in range(stock_w - prod_w + 1):
                for y in range(stock_h - prod_h + 1):
                    if self._can_place_(stock, (x, y), prod_size):
                        # Recursively calculate the remaining space after placement
                        remaining = max_remaining_space(stock, prod_size)
                        best_position = (x, y) if remaining is not None else None
                        if best_position:
                            dp[(stock_idx, remaining_space)] = best_position
                            return best_position

            return None

        # Loop through all sorted products
        for prod in sorted_prods:
            if prod["quantity"] > 0:
                prod_size = prod["size"]

                # Try placing the product in the best fitting stock using DP
                for i, stock in enumerate(observation["stocks"]):
                    remaining_space = self._get_stock_size_(stock)[0] * self._get_stock_size_(stock)[1]
                    pos = dp_solver(i, remaining_space, prod_size)

                    if pos is not None:
                        pos_x, pos_y = pos
                        stock_idx = i
                        break

                # If a valid placement is found, break the loop
                if stock_idx != -1:
                    break

        return {"stock_idx": stock_idx, "size": prod_size, "position": (pos_x, pos_y)}
"""
fmt.py — Centralized message formatting for re-drakos.
Single source of truth untuk semua tampilan bot.
"""


class Fmt:
    SEP   = "─" * 28
    SEP_S = "─" * 28

    # ── Status messages ──────────────────────────────────────────────────────
    @staticmethod
    def working(task: str) -> str:
        return f"<code>{task}...</code>"

    @staticmethod
    def progress(task: str, current: int, total: int) -> str:
        pct  = int((current / total) * 100) if total else 0
        fill = pct // 10
        bar  = "█" * fill + "░" * (10 - fill)
        return f"<code>{task}\n[{bar}] {pct}%  {current}/{total}</code>"

    @staticmethod
    def done(task: str, detail: str = "") -> str:
        line = f"{task}"
        if detail:
            line += f"\n{detail}"
        return f"<code>{line}</code>"

    @staticmethod
    def error(task: str, reason: str) -> str:
        return f"<code>{task}\nERR  {reason}</code>"

    @staticmethod
    def step(n: int, total: int, label: str) -> str:
        return f"<code>[{n}/{total}] {label}</code>"

    # ── Currency / balance ───────────────────────────────────────────────────
    @staticmethod
    def currency(data: dict, title: str = "BALANCE") -> str:
        items = data.get("currency", {})
        label_map = {
            "candles":          "Candles",
            "wax":              "Wax",
            "hearts":           "Hearts",
            "seasonal_candles": "Seasonal",
            "ascended_candles": "Ascended",
            "gift_candles":     "Gift CDL",
            "rebirths":         "Rebirths",
        }
        lines = [title, Fmt.SEP]
        for key, label in label_map.items():
            if key in items:
                lines.append(f"{label:<10}  {items[key]}")
        # Remaining keys not in map
        for key, val in items.items():
            if key not in label_map:
                lines.append(f"{key.replace('_',' ').title():<10}  {val}")
        lines.append(Fmt.SEP)
        return "<code>" + "\n".join(lines) + "</code>"

    @staticmethod
    def currency_diff(before: dict, after: dict, title: str = "RESULT") -> str:
        """Show before -> after delta, hanya field utama yang relevan."""
        b = before.get("currency", {})
        a = after.get("currency", {})

        # Hanya tampilkan field utama ini saja — buang color/event noise
        fields = [
            ("candles",          "Candles"),
            ("wax",              "Wax"),
            ("hearts",           "Hearts"),
            ("seasonal_candles", "Seasonal"),
            ("ascended_candles", "Ascended"),
            ("gift_candles",     "Gift CDL"),
            ("rebirths",         "Rebirths"),
        ]

        rows = []
        for key, label in fields:
            v_b = b.get(key)
            v_a = a.get(key)
            if v_b is None and v_a is None:
                continue
            v_b = v_b or 0
            v_a = v_a or 0
            delta = v_a - v_b
            sign  = "+" if delta >= 0 else ""
            delta_str = f" ({sign}{delta})" if delta != 0 else ""
            rows.append((label, v_b, v_a, delta_str))

        if not rows:
            return f"<code>{title}\n{Fmt.SEP}\nno data\n{Fmt.SEP}</code>"

        # Hitung lebar kolom secara dinamis
        lbl_w = max(len(r[0]) for r in rows)
        val_w = max(len(str(max(r[1], r[2]))) for r in rows)

        lines = [title, Fmt.SEP]
        for label, v_b, v_a, delta_str in rows:
            before_s = str(v_b).rjust(val_w)
            after_s  = str(v_a).rjust(val_w)
            lines.append(f"{label:<{lbl_w}}  {before_s} -> {after_s}{delta_str}")
        lines.append(Fmt.SEP)
        return "<code>" + "\n".join(lines) + "</code>"
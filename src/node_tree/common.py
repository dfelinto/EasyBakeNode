from __future__ import annotations


class TreeCtx(dict):
    def ensure_list(self, key) -> list:
        if key not in self:
            self[key] = []
        return self[key]

    def ensure_dict(self, key) -> TreeCtx:
        if key not in self:
            self[key] = TreeCtx()
        return self[key]

    def load(self, data) -> TreeCtx:
        for key, value in data.items():
            if isinstance(value, dict):
                self.ensure_dict(key).load(value)
            else:
                self[key] = value
        return self

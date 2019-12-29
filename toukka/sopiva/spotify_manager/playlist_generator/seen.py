#


class Seen(set):
    def is_in(self, item) -> bool:
        if item in self:
            return True
        else:
            return False

    def see(self, item) -> bool:
        if item in self:
            return True
        else:
            self.add(item)
            return False


# END

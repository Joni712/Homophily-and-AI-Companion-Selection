"""utils to control page sequence by rounds """


def task_page(task_id):
    """marks page to show only for specified task"""

    def task_class(cls):
        orig_displayed = getattr(cls, "is_displayed", lambda _: True)

        def is_displayed(player):
            return player.current_task == task_id and orig_displayed(player)

        cls.is_displayed = staticmethod(is_displayed)

        return cls

    return task_class


def round_page(round_num):
    """marks page to show only for specified round"""

    def task_class(cls):
        def is_displayed(player):
            return player.round_number == round_num

        cls.is_displayed = staticmethod(is_displayed)
        return cls

    return task_class

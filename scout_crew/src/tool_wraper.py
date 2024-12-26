class CrewAIToolWrapper:
    def __init__(self, tool):
        self.name = tool.name
        self.description = tool.description
        self.func = self._create_func(tool)

    def _create_func(self, tool):
        def func(*args, **kwargs):
            return tool(*args, **kwargs)
        return func
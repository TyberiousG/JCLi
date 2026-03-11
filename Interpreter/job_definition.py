class JobDefinition:
    def __init__(self, name, job_class, priority, user, program, arguments, output, steps=None):
        self.name = name
        self.job_class = job_class
        self.priority = priority
        self.user = user
        self.program = program
        self.arguments = arguments
        self.output = output
        self.steps = steps or []

    def __repr__(self):
        return (
            f"JobDefinition(name={self.name}, class={self.job_class}, priority={self.priority}, "
            f"user={self.user}, program={self.program}, args={self.arguments}, output={self.output}, "
            f"steps={self.steps})"
        )

    def to_dict(self):
        return {
            "name": self.name,
            "class": self.job_class,
            "priority": self.priority,
            "user": self.user,
            "program": self.program,
            "arguments": self.arguments,
            "output": self.output,
            "steps": self.steps,
        }

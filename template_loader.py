names = ["evaluator", "formulator", "manager", "programmer_variable", "programmer_constraints", "programmer_objective"]
templates = {}

class TemplateLoader(dict):
    def __init__(self, template_path:str):
        super().__init__()
        self.load_template(template_path)
    
    def load_template(self, path:str):
        print('Loading...')

        for name in names:
            for each in ["_instruction", "_prompt"]:
                with open(path + name + each + "_template.txt") as f:
                    self[name + each] = f.read()
        with open(path + "prep_code.txt") as f:
            self['prep_code'] = f.read()
        with open(path + "post_code.txt") as f:
            self['post_code'] = f.read()
        with open(path + "solver_prep_code.txt") as f:
            self['solver_prep_code'] = f.read()
from typing import Optional

# If Node is defined elsewhere, import it as well:
# from your_node_module import Node

class Context:
    next_var = 0

    # Pascal standard operators and functions
    stdlib_symbols = {
        # Arithmetic operators
        "+": "plus",
        "-": "minus",
        "*": "mult",
        "/": "div",
        "div": "integer_div",
        "mod": "mod",
        # Comparison operators
        "=": "eq",
        "<>": "neq",
        "<": "lt",
        "<=": "le",
        ">": "gt",
        ">=": "ge",
        # Logical operators
        "and": "and_op",
        "or": "or_op",
        "not": "not_op",
        # Assignment
        ":=": "assign",
        # Other operators
        "^": "pointer",
        "@": "address",
        ".": "dot",
        "..": "range",
        # Standard functions
        "abs": "abs",
        "sqr": "sqr",
        "sin": "sin",
        "cos": "cos",
        "exp": "exp",
        "ln": "ln",
        "sqrt": "sqrt",
        "chr": "chr",
        "ord": "ord",
        "pred": "pred",
        "succ": "succ",
        "round": "round",
        "trunc": "trunc",
        # Standard procedures
        "write": "write",
        "writeln": "writeln",
        "read": "read",
        "readln": "readln",
        # Standard types
        "integer": "type_integer",
        "real": "type_real",
        "boolean": "type_boolean",
        "char": "type_char",
        "string": "type_string",
        "array": "type_array",
        "record": "type_record",
        "file": "type_file",
        # Standard constants
        "true": "const_true",
        "false": "const_false",
        "nil": "const_nil",
    }

    def __init__(self, scope_name="", param_name="", parent=None):
        # Parent context (for nested scopes)
        self.parent = parent

        # Copy symbols from parent or create new symbol table
        self.symbols = {} if parent is None else parent.symbols.copy()

        # Current scope information
        self.scope_name = scope_name  # function/procedure/program name
        self.param_name = param_name  # parameter name if in a parameter context

        # Type information
        self.types = {}

        # Variable tracking
        self.variables = {}
        self.var_addresses = {}
        self.next_addr = 0

        # Constants
        self.constants = {}

        # Current scope level (0 for global)
        self.level = 0 if parent is None else parent.level + 1

        # Procedures table
        self.procedures = {}
        self.functions = {}

        # VM code generation
        self.label_counter = 0
        self.var_address = 0

    def in_global_scope(self):
        """Check if we're in the global scope (program level)"""
        return self.parent is None

    def next_variable(self):
        """Generate a new unique temporary variable name"""
        result = f"temp_{Context.next_var}"
        Context.next_var += 1
        return result

    def add_symbol(self, name, symbol_type, symbol_info=None):
        """Add a symbol to the current context"""
        self.symbols[name] = {
            "type": symbol_type,  # 'variable', 'function', 'procedure', 'constant', 'type'
            "info": symbol_info,  # type info, parameters, etc.
            "level": self.level,  # scope level
        }

    def lookup_symbol(self, name):
        """Look up a symbol in the current context or parent contexts"""
        if name in self.symbols:
            return self.symbols[name]
        elif name in self.stdlib_symbols:
            return {"type": "builtin", "info": self.stdlib_symbols[name]}
        elif self.parent:
            return self.parent.lookup_symbol(name)
        return None

    def add_variable(self, name, var_type, is_reference=False):
        """Add a variable to the current scope"""
        self.add_symbol(name, "variable", var_type)

    def add_constant(self, name, const_type, value):
        """Add a constant to the current scope"""
        self.constants[name] = {"type": const_type, "value": value}
        self.add_symbol(name, "constant", {"type": const_type, "value": value})

    def add_type(self, name, type_info):
        """Add a user-defined type to the current scope"""
        self.types[name] = type_info
        self.add_symbol(name, "type", type_info)

    def add_array(self, name, element_type, size=None):
        """Add an array to the current scope"""
        if size is None:
            size = 0
        self.add_symbol(
            name, "array", {"element_type": element_type, "size": size}
        )

    def add_function(self, name, return_type, parameters=None):
        """Add a function to the current scope"""
        if parameters is None:
            parameters = []
        self.add_symbol(
            name, "function", {"return_type": return_type, "parameters": parameters}
        )

    def add_procedure(self, name: str, parameters=None, block=None):
        """Add a procedure to the current scope."""
        if parameters is None:
            parameters = []
        # 1) Record in symbols exactly like add_function does:
        self.add_symbol(
            name, 
            "procedure", 
            {
                "parameters": parameters,
                "block": block,           # store the AST node or code block
                "return_type": None       # procedures don’t return a value
            }
        )
        # 2) (Optional) Keep a separate lookup of name→block for quick access:
        self.procedures[name.lower()] = block


    def get_procedure(self, name: str) :
        return self.procedures.get(name.lower())

    def create_child_scope(self, scope_name="", param_name=""):
        """Create a new child scope"""
        return Context(scope_name, param_name, self)

    def get_full_scope_path(self):
        """Get the full scope path (for debugging or symbol naming)"""
        if self.parent is None:
            return self.scope_name
        parent_path = self.parent.get_full_scope_path()
        if parent_path and self.scope_name:
            return f"{parent_path}.{self.scope_name}"
        return parent_path or self.scope_name

    def get_next_label(self) -> int:
        """Get next unique label number for VM code generation"""
        self.label_counter += 1
        return self.label_counter

    def get_next_var_address(self) -> int:
        """Get next available variable address"""
        addr = self.var_address
        self.var_address += 1
        return addr

    def get_var_address(self, var_name: str) -> int:
        """Get address for a variable, allocate if not exists"""
        if var_name not in self.var_addresses:
            self.var_addresses[var_name] = self.next_addr
            self.next_addr += 1
        return self.var_addresses[var_name]
    
    def get_var_type(self, var_name: str) -> Optional[str]:
        """Get the type of a variable"""
        if var_name in self.variables:
            return self.variables[var_name]["type"]
        symbol = self.lookup_symbol(var_name)
        if symbol and symbol["type"] == "variable":
            return symbol["info"]
        return None
    
    def is_function(self, name: str):

        """Check if a symbol is a function"""
        symbol = self.lookup_symbol("func" + name)
        return symbol is not None and symbol["type"] == "function"

    def is_procedure(self,name:str):
        symbol = self.lookup_symbol("proc" + name)
        return symbol is not None and symbol["type"] == "procedure"

    def allocate_var_address(self, var_name: str) -> int:
        """Allocate new address for variable"""
        addr = self.next_addr
        self.var_addresses[var_name] = addr
        self.next_addr += 1
        return addr

    def get_array_base_address(self, array_name: str) -> int:
        # Get the base address for an array variable
        return self.get_var_address(array_name)

    def allocate_array(self, array_name: str, size: int) -> int:
        # Allocate space for an array and return its base address
        base_addr = self.next_addr  # Fixed: next_address -> next_addr
        self.var_addresses[array_name] = base_addr
        self.next_addr += size  # Fixed: next_address -> next_addr
        return base_addr

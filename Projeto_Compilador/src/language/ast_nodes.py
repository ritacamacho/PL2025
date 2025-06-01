from typing import List, Tuple, Optional
from graphviz import Graph
from language.compiler_context import Context


class Node:
    def __init__(self, type, children=None, leaf=None):
        self.type = type
        self.children = children if children else []
        self.leaf = leaf

    def _to_string(self, level=0):
        ret = "  " * level + self.type
        if self.leaf is not None:
            ret += ": " + str(self.leaf)
        ret += "\n"
        for child in self.children:
            if isinstance(child, Node):
                ret += child._to_string(level + 1)
            else:
                # Handle non-Node children (e.g., strings)
                ret += "  " * (level + 1) + str(child) + "\n"
        return ret

    def to_vm(self, context: Context) -> None:
        print(f"VM code conversion not implemented for the {self.type} node type")

    def __str__(self):
        return self._to_string()


class ProgramNode(Node):
    def __init__(self, heading, block):
        super().__init__("program", [heading, block])
        self.heading = heading
        self.block = block

    def to_string(self, context: Context) -> str:
        return f"{self.heading.to_string(context)}{self.block.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        return "\n".join(line for line in self.block.to_vm(context, True).split("\n") if line.strip())

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ProgramNode)
            and self.heading == other.heading
            and self.block == other.block
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        heading_id = self.heading.append_to_graph(graph)
        block_id = self.block.append_to_graph(graph)
        graph.edge(str(node_id), str(heading_id))
        graph.edge(str(node_id), str(block_id))
        return node_id


class ProgramHeadingNode(Node):
    def __init__(self, identifier):
        super().__init__("programHeading", [identifier])
        self.identifier = identifier

    def to_string(self, context) -> str:
        return f"program {self.identifier.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        # Program heading doesn't generate VM code
        return ""

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ProgramHeadingNode)
            and self.identifier == other.identifier
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        identifier_id = self.identifier.append_to_graph(graph)
        graph.edge(str(node_id), str(identifier_id))
        return node_id


class IdentifierNode(Node):
    def __init__(self, value: str):
        super().__init__("identifier", [], value)
        self.value = value

    def to_string(self, context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        # Get variable address and load its value from global memory
        addr = context.get_var_address(self.value)
        return f"PUSHG {addr}"

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, IdentifierNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class BlockNode(Node):
    def __init__(self, declarations, compound_stmt):
        super().__init__("block", [declarations, compound_stmt])
        self.declarations = declarations
        self.compound_stmt = compound_stmt

    def to_string(self, context) -> str:
        decls = self.declarations.to_string(context)
        return f"{decls}\n{self.compound_stmt.to_string(context)}"

    def to_vm(self, context: Context, in_global_scope: bool) -> str:
        variable_decls = ""
        function_decls = ""
        
        for decl in self.declarations.declarations:
            if isinstance(decl, VariableDeclarationBlock):
                # Handle variable declarations
                variable_decls += decl.to_vm(context) + "\n"
            else:
                function_decls += decl.to_vm(context) + "\n"

        stmts = self.compound_stmt.to_vm(context)

        if in_global_scope:
            return f"{variable_decls}\nSTART\n{stmts}\nSTOP\n{function_decls}".strip()
        else:
            return f"{variable_decls}\n{stmts}".strip()


    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, BlockNode) and self.declarations == other.declarations

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        decl_id = self.declarations.append_to_graph(graph)
        stmt_id = self.compound_stmt.append_to_graph(graph)
        graph.edge(str(node_id), str(decl_id))
        graph.edge(str(node_id), str(stmt_id))
        return node_id


class DeclarationsNode(Node):
    def __init__(self, declarations=None):
        super().__init__("declarations", declarations if declarations else [])
        self.declarations = declarations if declarations else []


    def to_string(self, context) -> str:
        if not self.declarations:
            return ""  # Empty declarations
        return "\n".join(decl.to_string(context) for decl in self.declarations)

    def to_vm(self, context: Context) -> str:
        vm_code = []
        for decl in self.declarations:
            if isinstance(decl, VariableDeclarationBlock):
                # TODO: Append to vm code
                decl.to_vm(context)
            if not isinstance(decl, VariableDeclarationBlock):
                vm_code.append(decl.to_vm(context))
        return "\n".join(vm_code).strip()

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, DeclarationsNode)
            and self.declarations == other.declarations
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for decl in self.declarations:
            decl_id = decl.append_to_graph(graph)
            graph.edge(str(node_id), str(decl_id))
        return node_id


class CompoundStatementNode(Node):
    def __init__(self, statements):
        super().__init__("compoundStatement", [statements])
        self.statements = statements

    def to_string(self, context) -> str:
        return f"begin\n    {self.statements.to_string(context)}\nend"

    def to_vm(self, context: Context) -> str:
        return self.statements.to_vm(context).strip()

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, CompoundStatementNode)
            and self.statements == other.statements
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        stmt_id = self.statements.append_to_graph(graph)
        graph.edge(str(node_id), str(stmt_id))
        return node_id


class StatementsNode(Node):
    def __init__(self, statements: List[Node]):
        super().__init__("statements", statements)
        self.statements = statements

    def to_string(self, context) -> str:
        return ";\n    ".join(stmt.to_string(context) for stmt in self.statements)

    def to_vm(self, context: Context) -> str:
        return "\n".join(
            stmt.to_vm(context) for stmt in self.statements if stmt
        ).strip()

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, StatementsNode) and self.statements == other.statements

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for stmt in self.statements:
            stmt_id = stmt.append_to_graph(graph)
            graph.edge(str(node_id), str(stmt_id))
        return node_id


class CallStatementNode(Node):
    def __init__(self, identifier, expr_list):
        super().__init__("callStatement", [identifier, expr_list])
        self.identifier = identifier
        self.expr_list = expr_list

    def to_string(self, context) -> str:
        return (
            f"{self.identifier.to_string(context)}({self.expr_list.to_string(context)})"
        )

    def to_vm(self, context: Context) -> str:
        proc_name = self.identifier.value.lower()


        if proc_name == "writeln" or proc_name =="write":
            vm_code = []
            for expr in self.expr_list.expressions:
                vm_code.append(expr.to_vm(context))                
                if isinstance(expr, StringNode):
                    vm_code.append("WRITES")
                else:
                    if isinstance(expr, SimpleExpressionNode):
                        pass
                    elif context.get_var_type(expr.identifier.value) == "real":
                        vm_code.append("WRITEF")
                    elif context.get_var_type(expr.identifier.value) == "string":
                        vm_code.append("WRITES")
                    else:
                        vm_code.append("WRITEI")
            vm_code.append("WRITELN")
            return "\n".join(vm_code)
        elif proc_name == "readln":
            var = self.expr_list.expressions[0]
            var_addr = context.get_var_address(var.identifier.value)
            var_type = context.get_var_type(var.identifier.value)

            if isinstance(var.identifier, IndexedVariableNode):
                return f"READ\nATOI\nSTORE 2"

            conversion = "" 
            if var_type == "Integer" or var_type=="integer":
                conversion = "ATOI\n"

            return f"READ\n{conversion}STOREG {var_addr}"
        elif proc_name == "length":
            var = self.expr_list.expressions[0]
            var_addr = context.get_var_address(var.identifier.value)
            return f"PUSHG {var_addr}\nSTRLEN"
        else:
            # Handle user-defined procedures
            if context.is_function(self.identifier.value):
                return f"PUSHA func{self.identifier.value}\nCALL"
            elif context.is_procedure(self.identifier.value):
                return f"PUSHA proc{self.identifier.value}\nCALL"
            raise Exception(f"Undefined function: {self.identifier.value}")





class ExpressionListNode(Node):
    def __init__(self, expressions: List[Node]):
        super().__init__("expressionList", expressions)
        self.expressions = expressions

    def to_string(self, context) -> str:
        return ", ".join(expr.to_string(context) for expr in self.expressions)

    def to_vm(self, context: Context) -> str:
        return "\n".join(expr.to_vm(context) for expr in self.expressions)

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ExpressionListNode)
            and self.expressions == other.expressions
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for expr in self.expressions:
            expr_id = expr.append_to_graph(graph)
            graph.edge(str(node_id), str(expr_id))
        return node_id


class StringNode(Node):
    def __init__(self, value: str):
        super().__init__("string", [], value)
        self.value = value

    def to_string(self, context) -> str:
        return f"'{self.value}'"

    def to_vm(self, context: Context) -> str:
        return f'PUSHS "{self.value}"'

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, StringNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class EmptyStatementNode(Node):
    def __init__(self):
        super().__init__("emptyStatement", [])

    def to_string(self, context) -> str:
        return ""

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, EmptyStatementNode)

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        return node_id


class VariableDeclarationBlock(Node):
    def __init__(self, declarations: List[Node]):
        super().__init__("variableDeclarationBlock", declarations)
        self.declarations = declarations

    def to_string(self, context: Context) -> str:
        return "\n".join(decl.to_string(context) for decl in self.declarations)

    def to_vm(self, context: Context) -> str:
        vm_code = []
        for decl in self.declarations:
            for identifier in decl.identifier.identifiers:
                if isinstance(decl.type_node, ArrayTypeNode):
                    # This is an array declaration
                    if isinstance(decl.type_node.index_type, SubRangeTypeNode):
                        # Handle subrange type
                        index_type = decl.type_node.index_type
                        vm_code.append(f"ALLOC {index_type.upper_bound.value - index_type.lower_bound.value}")
                else:
                    context.add_variable(identifier.value, decl.type_node.value)
                
        return "\n".join(vm_code)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, VariableDeclarationBlock)
            and self.declarations == other.declarations
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for decl in self.declarations:
            decl_id = decl.append_to_graph(graph)
            graph.edge(str(node_id), str(decl_id))
        return node_id


class VariableDeclarationList(Node):
    def __init__(self, declarations=None):
        self.declarations = declarations if declarations else []
        # Pass declarations as children to Node constructor
        super().__init__("variableDeclarationList", children=self.declarations)

    def to_string(self, context: Context) -> str:
        return ", ".join(decl.to_string(context) for decl in self.declarations)

    def to_vm(self, context: Context) -> str:
        return "\n".join(decl.to_vm(context) for decl in self.declarations)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, VariableDeclarationList)
            and self.declarations == other.declarations
        )

    def __iter__(self):
        """Make this class iterable by returning an iterator over declarations"""
        return iter(self.declarations)

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)  # Use self.name instead of self.type
        for decl in self.declarations:
            decl_id = decl.append_to_graph(graph)
            graph.edge(str(node_id), str(decl_id))
        return node_id


class VariableDeclaration(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("variableDeclaration", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}: {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return f"ALLOC {self.identifier.value}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, VariableDeclaration)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class IdentifierListNode(Node):
    def __init__(self, identifiers: List[Node]):
        super().__init__("identifierList", identifiers)
        self.identifiers = identifiers

    def to_string(self, context: Context) -> str:
        return ", ".join(id.to_string(context) for id in self.identifiers)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, IdentifierListNode)
            and self.identifiers == other.identifiers
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for id in self.identifiers:
            id_id = id.append_to_graph(graph)
            graph.edge(str(node_id), str(id_id))
        return node_id


class TypeIdentifierNode(Node):
    def __init__(self, value: str):
        super().__init__("typeIdentifier", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, TypeIdentifierNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class VariableNode(Node):
    def __init__(self, identifier: Node):
        super().__init__("variable", [identifier])
        self.identifier = identifier

    def to_string(self, context: Context) -> str:
        return self.identifier.to_string(context)

    def to_vm(self, context: Context) -> str:
        if isinstance(self.identifier, IndexedVariableNode):
            # Handle indexed variable (array access)
            addr = context.get_var_address(self.identifier.identifier.value)
            index_code = self.identifier.index.to_vm(context)
            return f"// TODO: load indexed variable ({self.identifier.identifier.value}) value"
        if self.identifier.value and context.is_function(self.identifier.value):
            # This is actually a function with no arguments
            return f"PUSHA func{self.identifier.value}\nCALL"
        addr = context.get_var_address(self.identifier.value)
        return f"PUSHG {addr}  // Load {self.identifier.value}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, VariableNode) and self.identifier == other.identifier

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        return node_id


class IfStatementNode(Node):
    def __init__(self, condition: Node, then_block: Node, else_block: Node = None):
        super().__init__("ifStatement", [condition, then_block, else_block])
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def to_string(self, context: Context) -> str:
        if self.else_block:
            return f"if {self.condition.to_string(context)} then {self.then_block.to_string(context)} else {self.else_block.to_string(context)}"
        return f"if {self.condition.to_string(context)} then {self.then_block.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        label_count = context.get_next_label()
        else_label = f"ELSE{label_count}"
        end_label = f"ENDIF{label_count}"
        
        vm_code = []
        vm_code.append(self.condition.to_vm(context))
        vm_code.append(f"JZ {else_label}")
        vm_code.append(self.then_block.to_vm(context))
        
        if self.else_block:
            vm_code.append(f"JUMP {end_label}")
            vm_code.append(f"{else_label}:")
            vm_code.append(self.else_block.to_vm(context))
        else:
            vm_code.append(f"{else_label}:")
            
        vm_code.append(f"{end_label}:")
        return "\n".join(vm_code)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, IfStatementNode)
            and self.condition == other.condition
            and self.then_block == other.then_block
            and self.else_block == other.else_block
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        cond_id = self.condition.append_to_graph(graph)
        then_id = self.then_block.append_to_graph(graph)
        graph.edge(str(node_id), str(cond_id))
        graph.edge(str(node_id), str(then_id))
        if self.else_block:
            else_id = self.else_block.append_to_graph(graph)
            graph.edge(str(node_id), str(else_id))
        return node_id


class ExpressionNode(Node):
    def __init__(self, left: Node, right: Node, operator: Node):
        super().__init__("expression", [left, operator, right])
        self.left = left
        self.right = right
        self.operator = operator

    def to_string(self, context: Context) -> str:
        return f"{self.left.to_string(context)} {self.operator.to_string(context)} {self.right.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        # Generate VM code for left and right expressions
        left_code = self.left.to_vm(context)
        right_code = self.right.to_vm(context)

        # Map operators to VM instructions
        op_map = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "mod": "MOD",
            "and": "AND",
            "div": "DIV",
            "or": "OR",
        }

        if isinstance(self.operator, RelationalOperatorNode):
            return f"{left_code}\n{right_code}\n{self.operator.to_vm(context)}"

        op = op_map.get(self.operator.value, "NOP")

        return f"{left_code}\n{right_code}\n{op}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ExpressionNode)
            and self.left == other.left
            and self.right == other.right
            and self.operator == other.operator
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        left_id = self.left.append_to_graph(graph)
        op_id = self.operator.append_to_graph(graph)
        right_id = self.right.append_to_graph(graph)
        graph.edge(str(node_id), str(left_id))
        graph.edge(str(node_id), str(op_id))
        graph.edge(str(node_id), str(right_id))
        return node_id


class AssigmentStatementNode(Node):
    def __init__(self, variable: Node, expression: Node):
        super().__init__("assignmentStatement", [variable, expression])
        self.variable = variable
        self.expression = expression

    def to_string(self, context: Context) -> str:
        return f"{self.variable.to_string(context)} := {self.expression.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        # Generate expression code
        expr_code = self.expression.to_vm(context)
        # Get variable address
        var_addr = context.get_var_address(self.variable.identifier.value)
        return f"{expr_code}\nSTOREG {var_addr}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, AssigmentStatementNode)
            and self.variable == other.variable
            and self.expression == other.expression
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        var_id = self.variable.append_to_graph(graph)
        expr_id = self.expression.append_to_graph(graph)
        graph.edge(str(node_id), str(var_id))
        graph.edge(str(node_id), str(expr_id))
        return node_id


class RelationalOperatorNode(Node):
    def __init__(self, value: str):
        super().__init__("relationalOperator", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        op_map = {
            ">": "SUP",
            "<": "INF",
            ">=": "SUPEQ",
            "<=": "INFEQ",
            "=": "EQUAL",
            "<>": "EQUAL\nNOT",
        }
        return op_map.get(self.value, "NOP")

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, RelationalOperatorNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class ForStatementNode(Node):
    def __init__(
        self,
        identifier: Node,
        start_expr: Node,
        end_expr: Node,
        block: Node,
        direction: str,
    ):
        super().__init__("forStatement", [identifier, start_expr, end_expr, block])
        self.identifier = identifier
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.block = block
        self.direction = direction.lower()  # "to" or "downto"

    def to_string(self, context: Context) -> str:
        return (
            f"for {self.identifier.to_string(context)} := {self.start_expr.to_string(context)} "
            f"{self.direction} {self.end_expr.to_string(context)} do {self.block.to_string(context)}"
        )

    def to_vm(self, context: Context) -> str:
        label_count = context.get_next_label()
        loop_label = f"loop{label_count}"
        end_label = f"endloop{label_count}"
        var_addr = context.get_var_address(self.identifier.value)

        vm_code = []

        # Initialize loop variable
        vm_code.append(self.start_expr.to_vm(context))  # Push initial value (1)
        vm_code.append(f"STOREG {var_addr}")  # Store in i

        # Loop start
        vm_code.append(f"{loop_label}:")

        # Compare loop variable with end value
        vm_code.append(f"PUSHG {var_addr}")  # Push current value of i
        vm_code.append(self.end_expr.to_vm(context))  # Push n

        if self.direction == "to":
            vm_code.append("INFEQ")  # i <= n
        else:
            vm_code.append("SUPEQ")  # i >= n

        vm_code.append(f"JZ {end_label}")  # If false, exit loop

        # Execute loop body
        vm_code.append(self.block.to_vm(context))

        # Increment or decrement counter
        vm_code.append(f"PUSHG {var_addr}")  # Push i
        if self.direction == "to":
            vm_code.append("PUSHI 1")
            vm_code.append("ADD")  # i + 1
        else:
            vm_code.append("PUSHI 1")
            vm_code.append("SUB")  # i - 1
        vm_code.append(f"STOREG {var_addr}")  # Store new i

        # Continue loop
        vm_code.append(f"JUMP {loop_label}")
        vm_code.append(f"{end_label}:")

        return "\n".join(vm_code)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ForStatementNode)
            and self.identifier == other.identifier
            and self.start_expr == other.start_expr
            and self.end_expr == other.end_expr
            and self.block == other.block
            and self.direction == other.direction
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name} ({self.direction})")
        id_id = self.identifier.append_to_graph(graph)
        start_id = self.start_expr.append_to_graph(graph)
        end_id = self.end_expr.append_to_graph(graph)
        block_id = self.block.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(start_id))
        graph.edge(str(node_id), str(end_id))
        graph.edge(str(node_id), str(block_id))
        return node_id


class TermNode(Node):
    def __init__(self, left: Node, right: Node, operator: Node):
        super().__init__("term", [left, operator, right])
        self.left = left
        self.right = right
        self.operator = operator

    def to_string(self, context: Context) -> str:
        return f"{self.left.to_string(context)} {self.operator.to_string(context)} {self.right.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        left_code = self.left.to_vm(context)
        right_code = self.right.to_vm(context)
        op_map = {
            "*": "MUL",
            "/": "DIV", 
            "div": "DIV",
            "mod": "MOD",
            "and": "AND"
        }
        op = op_map.get(self.operator.value.lower(), "NOP")
        return f"{left_code}\n{right_code}\n{op}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, TermNode)
            and self.left == other.left
            and self.right == other.right
            and self.operator == other.operator
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        left_id = self.left.append_to_graph(graph)
        op_id = self.operator.append_to_graph(graph)
        right_id = self.right.append_to_graph(graph)
        graph.edge(str(node_id), str(left_id))
        graph.edge(str(node_id), str(op_id))
        graph.edge(str(node_id), str(right_id))
        return node_id


class ConstantDefinitionBlock(Node):
    def __init__(self, definitions: List[Node]):
        super().__init__("constantDefinitionBlock", definitions)
        self.definitions = definitions

    def to_string(self, context: Context) -> str:
        return "\n".join(defn.to_string(context) for defn in self.definitions)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ConstantDefinitionBlock)
            and self.definitions == other.definitions
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for defn in self.definitions:
            defn_id = defn.append_to_graph(graph)
            graph.edge(str(node_id), str(defn_id))
        return node_id


class ConstantDefinitionList(Node):
    def __init__(self, definitions=None):
        self.definitions = definitions if definitions else []
        # Pass definitions
        super().__init__("constantDefinitionList", children=self.definitions)

    def to_string(self, context: Context) -> str:
        return ", ".join(defn.to_string(context) for defn in self.definitions)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ConstantDefinitionList)
            and self.definitions == other.definitions
        )

    def __iter__(self):
        """Make this class iterable by returning an iterator over definitions"""
        return iter(self.definitions)

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for defn in self.definitions:
            defn_id = defn.append_to_graph(graph)
            graph.edge(str(node_id), str(defn_id))
        return node_id


class ConstantDefinition(Node):
    def __init__(self, identifier: Node, value: Node):
        super().__init__("constantDefinition", [identifier, value])
        self.identifier = identifier
        self.value = value

    def to_string(self, context: Context) -> str:
        return (
            f"{self.identifier.to_string(context)} = {self.value.to_string(context)};"
        )

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ConstantDefinition)
            and self.identifier == other.identifier
            and self.value == other.value
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        val_id = self.value.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(val_id))
        return node_id


class ConstantNode(Node):
    def __init__(self, value: str):
        super().__init__("constant", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        return f'PUSHS "{self.value}"'

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, ConstantNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class UnsignedIntegerNode(Node):
    def __init__(self, value: str):
        super().__init__("unsignedInteger", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        return f"PUSHI {self.value}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, UnsignedIntegerNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id
    
    def get_value(self) -> int:
        """Returns the integer value of this node."""
        return int(self.value)


class UnsignedRealNode(Node):
    def __init__(self, value: str):
        super().__init__("unsignedReal", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        return f"PUSHF {self.value}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, UnsignedRealNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class SignNode(Node):
    def __init__(self, value: str):
        super().__init__("sign", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        return (
            ""  # Sign application usually handled in ConstantNode or arithmetic logic
        )

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, SignNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class ConstantChrNode(Node):
    def __init__(self, value: str):
        super().__init__("constantChr", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        return f'PUSHS "{self.value}"'

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, ConstantChrNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class TypeDeclarationBlock(Node):
    def __init__(self, declarations: List[Node]):
        super().__init__("typeDeclarationBlock", declarations)
        self.declarations = declarations

    def to_string(self, context: Context) -> str:
        return "\n".join(decl.to_string(context) for decl in self.declarations)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, TypeDeclarationBlock)
            and self.declarations == other.declarations
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for decl in self.declarations:
            decl_id = decl.append_to_graph(graph)
            graph.edge(str(node_id), str(decl_id))
        return node_id


class TypeDefinitionList(Node):
    def __init__(self, definitions=None):
        self.definitions = definitions if definitions else []
        # Pass definitions
        super().__init__("typeDefinitionList", children=self.definitions)

    def to_string(self, context: Context) -> str:
        return ", ".join(defn.to_string(context) for defn in self.definitions)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, TypeDefinitionList)
            and self.definitions == other.definitions
        )

    def __iter__(self):
        """Make this class iterable by returning an iterator over definitions"""
        return iter(self.definitions)

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for defn in self.definitions:
            defn_id = defn.append_to_graph(graph)
            graph.edge(str(node_id), str(defn_id))
        return node_id


class TypeDefinition(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("typeDefinition", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)} = {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, TypeDefinition)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class ScalarTypeNode(Node):
    def __init__(self, value: str):
        super().__init__("scalarType", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, ScalarTypeNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class SubRangeTypeNode(Node):
    def __init__(self, lower_bound: Node, upper_bound: Node):
        super().__init__("subRangeType", [lower_bound, upper_bound])
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def to_string(self, context: Context) -> str:
        return f"[{self.lower_bound.to_string(context)}..{self.upper_bound.to_string(context)}]"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, SubRangeTypeNode)
            and self.lower_bound == other.lower_bound
            and self.upper_bound == other.upper_bound
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        lower_id = self.lower_bound.append_to_graph(graph)
        upper_id = self.upper_bound.append_to_graph(graph)
        graph.edge(str(node_id), str(lower_id))
        graph.edge(str(node_id), str(upper_id))
        return node_id


class StringTypeNode(Node):
    def __init__(self, length: Node):
        super().__init__("stringType", [length])
        self.length = length

    def to_string(self, context: Context) -> str:
        return f"string[{self.length.to_string(context)}]"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, StringTypeNode) and self.length == other.length

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        length_id = self.length.append_to_graph(graph)
        graph.edge(str(node_id), str(length_id))
        return node_id


class ArrayTypeNode(Node):
    def __init__(self, index_type: Node, element_type: Node):
        super().__init__("arrayType", [index_type, element_type])
        self.index_type = index_type
        self.element_type = element_type

    def to_string(self, context: Context) -> str:
        return f"array[{self.index_type.to_string(context)}] of {self.element_type.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ArrayTypeNode)
            and self.index_type == other.index_type
            and self.element_type == other.element_type
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        index_id = self.index_type.append_to_graph(graph)
        element_id = self.element_type.append_to_graph(graph)
        graph.edge(str(node_id), str(index_id))
        graph.edge(str(node_id), str(element_id))
        return node_id


class TypeListNode(Node):
    def __init__(self, types: List[Node]):
        super().__init__("typeList", types)
        self.types = types

    def to_string(self, context: Context) -> str:
        return ", ".join(type_node.to_string(context) for type_node in self.types)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, TypeListNode) and self.types == other.types

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for type_node in self.types:
            type_id = type_node.append_to_graph(graph)
            graph.edge(str(node_id), str(type_id))
        return node_id


class recordTypeNode(Node):
    def __init__(self, fields: List[Node]):
        super().__init__("recordType", fields)
        self.fields = fields

    def to_string(self, context: Context) -> str:
        return "{" + ", ".join(field.to_string(context) for field in self.fields) + "}"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, recordTypeNode) and self.fields == other.fields

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for field in self.fields:
            field_id = field.append_to_graph(graph)
            graph.edge(str(node_id), str(field_id))
        return node_id


class FieldListNode(Node):
    def __init__(self, fields: List[Node]):
        super().__init__("fieldList", fields)
        self.fields = fields

    def to_string(self, context: Context) -> str:
        return ", ".join(field.to_string(context) for field in self.fields)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, FieldListNode) and self.fields == other.fields

    def __iter__(self):
        """Make this class iterable by returning an iterator over fields"""
        return iter(self.fields)

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for field in self.fields:
            field_id = field.append_to_graph(graph)
            graph.edge(str(node_id), str(field_id))
        return node_id


class FixedPartNode(Node):
    def __init__(self, fields: List[Node]):
        super().__init__("fixedPart", fields)
        self.fields = fields

    def to_string(self, context: Context) -> str:
        return ", ".join(field.to_string(context) for field in self.fields)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, FixedPartNode) and self.fields == other.fields

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for field in self.fields:
            field_id = field.append_to_graph(graph)
            graph.edge(str(node_id), str(field_id))
        return node_id


class RecordSectionList(Node):
    def __init__(self, sections: List[Node]):
        super().__init__("recordSectionList", sections)
        self.sections = sections

    def to_string(self, context: Context) -> str:
        return ", ".join(section.to_string(context) for section in self.sections)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, RecordSectionList) and self.sections == other.sections

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for section in self.sections:
            section_id = section.append_to_graph(graph)
            graph.edge(str(node_id), str(section_id))
        return node_id


class RecordSectionNode(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("recordSection", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}: {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, RecordSectionNode)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class VariantPartNode(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("variantPart", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}: {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, VariantPartNode)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class TagNode(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("tag", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}: {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, TagNode)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class VariantListNode(Node):
    def __init__(self, tags: List[Node]):
        super().__init__("variantList", tags)
        self.tags = tags

    def to_string(self, context: Context) -> str:
        return ", ".join(tag.to_string(context) for tag in self.tags)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, VariantListNode) and self.tags == other.tags

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for tag in self.tags:
            tag_id = tag.append_to_graph(graph)
            graph.edge(str(node_id), str(tag_id))
        return node_id


class VariantNode(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("variant", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}: {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, VariantNode)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class ConstListNode(Node):
    def __init__(self, constants: List[Node]):
        super().__init__("constList", constants)
        self.constants = constants

    def to_string(self, context: Context) -> str:
        return ", ".join(constant.to_string(context) for constant in self.constants)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, ConstListNode) and self.constants == other.constants

    def __iter__(self):
        """Make this class iterable by returning an iterator over constants"""
        return iter(self.constants)

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for constant in self.constants:
            constant_id = constant.append_to_graph(graph)
            graph.edge(str(node_id), str(constant_id))
        return node_id


class SetTypeNode(Node):
    def __init__(self, element_type: Node):
        super().__init__("setType", [element_type])
        self.element_type = element_type

    def to_string(self, context: Context) -> str:
        return f"set of {self.element_type.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, SetTypeNode) and self.element_type == other.element_type
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        type_id = self.element_type.append_to_graph(graph)
        graph.edge(str(node_id), str(type_id))
        return node_id


class ProcedureDeclarationNode(Node):
    def __init__(self, identifier: Node, params: Node, block: Node):
        super().__init__("procedureDeclaration", [identifier, params, block])
        self.identifier = identifier
        self.params = params
        self.block = block

    def to_string(self, context: Context) -> str:
        return f"procedure {self.identifier.to_string(context)}({self.params.to_string(context)}) {self.block.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ProcedureDeclarationNode)
            and self.identifier == other.identifier
            and self.params == other.params
            and self.block == other.block
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        params_id = self.params.append_to_graph(graph)
        block_id = self.block.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(params_id))
        graph.edge(str(node_id), str(block_id))
        return node_id


class FormalParameterListNode(Node):
    def __init__(self, parameters: List[Node]):
        super().__init__("formalParameterList", parameters)
        self.parameters = parameters

    def to_string(self, context: Context) -> str:
        return ", ".join(param.to_string(context) for param in self.parameters)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, FormalParameterListNode)
            and self.parameters == other.parameters
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for param in self.parameters:
            param_id = param.append_to_graph(graph)
            graph.edge(str(node_id), str(param_id))
        return node_id


class FormalParameterSectionListNode(Node):
    def __init__(self, sections: List[Node]):
        super().__init__("formalParameterSectionList", sections)
        self.sections = sections

    def to_string(self, context: Context) -> str:
        return ", ".join(section.to_string(context) for section in self.sections)

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, FormalParameterSectionListNode)
            and self.sections == other.sections
        )

    def __iter__(self):
        """Make this class iterable by returning an iterator over sections"""
        return iter(self.sections)

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        for section in self.sections:
            section_id = section.append_to_graph(graph)
            graph.edge(str(node_id), str(section_id))
        return node_id


class FormalParameterSectionNode(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("formalParameterSection", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}: {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, FormalParameterSectionNode)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class ParameterGroupNode(Node):
    def __init__(self, identifier: Node, type_node: Node):
        super().__init__("parameterGroup", [identifier, type_node])
        self.identifier = identifier
        self.type_node = type_node

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}: {self.type_node.to_string(context)};"

    def to_vm(self, context: Context) -> str:
        return ""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ParameterGroupNode)
            and self.identifier == other.identifier
            and self.type_node == other.type_node
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        type_id = self.type_node.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(type_id))
        return node_id


class FunctionDeclarationNode(Node):
    def __init__(self, identifier: Node, params: Node, return_type: Node, block: Node):        
        super().__init__("functionDeclaration", [identifier, params, return_type, block])
        self.identifier = identifier
        self.params = params
        self.return_type = return_type
        self.block = block

    def to_string(self, context: Context) -> str:
        params = self.params.to_string(context) if self.params else ""
        return f"function {self.identifier.to_string(context)}{params}: {self.return_type.to_string(context)};\n{self.block.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        safe_function_identifier = self.identifier.value
        # Get unique label for function
        func_label = f"func{safe_function_identifier}"

        context.add_function(func_label, self.return_type.value, self.params)
        
        # Store function parameters
        param_setup = []
        if self.params and not isinstance(self.params, EmptyStatementNode):
            for i, param in enumerate(self.params.parameters):
                addr = context.allocate_var_address(safe_function_identifier)

        vm_code = [
            f"{func_label}:",  # Function label
        ]
        
        # Add parameter setup code
        vm_code.extend(param_setup)
        
        # Add function body code
        vm_code.append(self.block.to_vm(context, False))
        
        # Add return sequence
        vm_code.extend([
            "RETURN"
        ])
        
        return "\n".join(vm_code)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, FunctionDeclarationNode)
            and self.identifier == other.identifier
            and self.params == other.params
            and self.return_type == other.return_type
            and self.block == other.block
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        params_id = self.params.append_to_graph(graph)
        return_type_id = self.return_type.append_to_graph(graph)
        block_id = self.block.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(params_id))
        graph.edge(str(node_id), str(return_type_id))
        graph.edge(str(node_id), str(block_id))
        return node_id


class IndexedVariableNode(Node):
    def __init__(self, identifier: Node, index: Node):
        super().__init__("indexedVariable", [identifier, index])
        self.identifier = identifier
        self.index = index
        self.value = None

    def to_string(self, context: Context) -> str:
        return f"{self.identifier.to_string(context)}[{self.index.to_string(context)}]"

    def to_vm(self, context: Context) -> str:
        # Get base address for array
        base_addr = context.get_array_base_address(self.identifier.value)

        # Generate code for index computation
        index_code = self.index.to_vm(context)

        # Load value from array at computed index
        return f"""{index_code}     // Compute index
PUSHI {base_addr}  // Array base address
ADD           // Calculate array offset
LOADN         // Load value from array"""

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, IndexedVariableNode)
            and self.identifier == other.identifier
            and self.index == other.index
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        id_id = self.identifier.append_to_graph(graph)
        index_id = self.index.append_to_graph(graph)
        graph.edge(str(node_id), str(id_id))
        graph.edge(str(node_id), str(index_id))
        return node_id


class SimpleExpressionNode(Node):
    def __init__(
        self, left: Node, operator: Optional[Node] = None, right: Optional[Node] = None
    ):
        children = (
            [left]
            if not operator
            else [left, operator] if not right else [left, operator, right]
        )
        super().__init__("simpleExpression", children)
        self.left = left
        self.operator = operator
        self.right = right

    def to_string(self, context: Context) -> str:
        if self.operator and self.right:
            return f"{self.left.to_string(context)} {self.operator.to_string(context)} {self.right.to_string(context)}"
        elif self.operator:  # unary case
            return f"{self.operator.to_string(context)}{self.left.to_string(context)}"
        else:
            return self.left.to_string(context)

    def to_vm(self, context: Context) -> str:
        if self.operator and self.right:
            left_code = self.left.to_vm(context)
            right_code = self.right.to_vm(context)
            op_code = self.operator.to_vm(context)
            return f"{left_code}\n{right_code}\n{op_code}"
        elif self.operator:
            term_code = self.left.to_vm(context)
            if self.operator.value == "-":
                return f"{term_code}\nNEG"
            else:
                return term_code  # + sign is no-op
        else:
            return self.left.to_vm(context)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, SimpleExpressionNode)
            and self.left == other.left
            and self.operator == other.operator
            and self.right == other.right
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        graph.edge(str(node_id), str(self.left.append_to_graph(graph)))
        if self.operator:
            graph.edge(str(node_id), str(self.operator.append_to_graph(graph)))
        if self.right:
            graph.edge(str(node_id), str(self.right.append_to_graph(graph)))
        return node_id


class AdditionOperatorNode(Node):
    def __init__(self, value: str):
        super().__init__("additionOperator", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        op_map = {"+": "ADD", "-": "SUB", "or": "OR"}
        return op_map.get(self.value, "NOP")

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, AdditionOperatorNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class MultiplicativeOperatorNode(Node):
    def __init__(self, value: str):
        super().__init__("multiplicativeOperator", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        op_map = {"*": "MUL", "/": "DIV", "div": "DIV", "mod": "MOD", "and": "AND"}
        return op_map.get(self.value.lower(), "NOP")

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, MultiplicativeOperatorNode) and self.value == other.value
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class FactorNode(Node):
    def __init__(self, value: str):
        super().__init__("factor", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return self.value

    def to_vm(self, context: Context) -> str:
        if isinstance(self.value, (int, float)):
            return f"PUSHI {self.value}"
        return self.value.to_vm(context)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, FactorNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class UnsignedConstantNode(Node):
    def __init__(self, value):
        super().__init__("unsignedConstant", [], value)
        self.value = value

    def to_string(self, context: Context) -> str:
        return str(self.value)

    def to_vm(self, context: Context) -> str:
        if isinstance(self.value, bool):
            return f"PUSHI {1 if self.value else 0}"
        elif isinstance(self.value, (int, float)):
            return f"PUSHI {self.value}"
        elif isinstance(self.value, str):
            return f'PUSHS "{self.value}"'
        return str(self.value)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, UnsignedConstantNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class WhileStatementNode(Node):
    def __init__(self, condition: Node, block: Node):
        super().__init__("whileStatement", [condition, block])
        self.condition = condition
        self.block = block

    def to_string(self, context: Context) -> str:
        return f"while {self.condition.to_string(context)} do {self.block.to_string(context)}"

    def to_vm(self, context: Context) -> str:
        label_count = context.get_next_label()
        start_label = f"WHILE{label_count}"
        end_label = f"ENDWHILE{label_count}"
        vm_code = []
        vm_code.append(f"{start_label}:")
        # Evaluate condition
        vm_code.append(self.condition.to_vm(context))
        vm_code.append(f"JZ {end_label}")
        # Loop body
        vm_code.append(self.block.to_vm(context))
        # Jump back to start
        vm_code.append(f"JUMP {start_label}")
        vm_code.append(f"{end_label}:")
        return "\n".join(line for line in vm_code if line.strip())


    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, WhileStatementNode)
            and self.condition == other.condition
            and self.block == other.block
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        condition_id = self.condition.append_to_graph(graph)
        block_id = self.block.append_to_graph(graph)
        graph.edge(str(node_id), str(condition_id))
        graph.edge(str(node_id), str(block_id))
        return node_id


class BooleanConstantNode(Node):
    def __init__(self, value: bool):
        super().__init__("boolean", [], str(value).lower())
        self.value = value

    def to_vm(self, context):
        return f"PUSHI {1 if self.value else 0}"

    def to_string(self, context):
        return "true" if self.value else "false"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return isinstance(other, BooleanConstantNode) and self.value == other.value

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), f"{self.name}: {self.value}")
        return node_id


class ParenthesizedExpressionNode(Node):
    def __init__(self, expression: Node):
        super().__init__("parenthesizedExpression", [expression])
        self.expression = expression

    def to_string(self, context: Context) -> str:
        return f"({self.expression.to_string(context)})"

    def to_vm(self, context: Context) -> str:
        # Just evaluate the inner expression
        return self.expression.to_vm(context)

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, ParenthesizedExpressionNode)
            and self.expression == other.expression
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        expression_id = self.expression.append_to_graph(graph)
        graph.edge(str(node_id), str(expression_id))
        return node_id


class FormattedExpressionNode(Node):
    def __init__(
        self, variable: Node, expression: Node, format_expression: Optional[Node] = None
    ):
        children = (
            [variable, expression]
            if not format_expression
            else [variable, expression, format_expression]
        )
        super().__init__("formattedExpression", children)
        self.variable = variable
        self.expression = expression
        self.format_expression = format_expression

    def to_string(self, context: Context) -> str:
        if self.format_expression:
            return f"{self.variable.to_string(context)}:{self.expression.to_string(context)}:{self.format_expression.to_string(context)}"
        return (
            f"{self.variable.to_string(context)}:{self.expression.to_string(context)}"
        )

    def to_vm(self, context: Context) -> str:
        # Generate code for variable and expression
        var_code = self.variable.to_vm(context)
        expr_code = self.expression.to_vm(context)

        # If there's a format expression, include it
        if self.format_expression:
            format_code = self.format_expression.to_vm(context)
            return f"{var_code}\n{expr_code}\n{format_code}"
        return f"{var_code}\n{expr_code}"

    def validate(self, context: Context) -> Tuple[bool, List[str]]:
        return True, []

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, FormattedExpressionNode)
            and self.variable == other.variable
            and self.expression == other.expression
            and self.format_expression == other.format_expression
        )

    def append_to_graph(self, graph: Graph) -> int:
        node_id = len(graph.body)
        graph.node(str(node_id), self.name)
        var_id = self.variable.append_to_graph(graph)
        expr_id = self.expression.append_to_graph(graph)
        graph.edge(str(node_id), str(var_id))
        graph.edge(str(node_id), str(expr_id))
        if self.format_expression:
            format_id = self.format_expression.append_to_graph(graph)
            graph.edge(str(node_id), str(format_id))
        return node_id

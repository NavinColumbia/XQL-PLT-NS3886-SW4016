import os
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.sql = ""

    def generate(self):
        self.sql = self.process_query(self.ast)
        return self.sql

    def process_query(self, node):
        query_parts = []

        select_clause = self.process_select(node.select)
        query_parts.append(select_clause)

        from_clause = self.process_from(node.from_)
        query_parts.append(from_clause)

        if node.where:
            where_clause = self.process_where(node.where)
            query_parts.append(where_clause)

        if node.group_by:
            group_by_clause = self.process_group_by(node.group_by)
            query_parts.append(group_by_clause)

        if node.having:
            having_clause = self.process_having(node.having)
            query_parts.append(having_clause)

        if node.order_by:
            order_by_clause = self.process_order_by(node.order_by)
            query_parts.append(order_by_clause)

        return " ".join(query_parts)

    def process_select(self, node):
        columns = []
        for col in node.columns:
            columns.append(self.process_column(col))
        return "SELECT " + ", ".join(columns)

    def process_column(self, node):
        if isinstance(node.value, str):
            if ' ' in node.value:
                raise CodeGenError(f"Invalid column name '{node.value}'. Column names cannot contain spaces.", node)
            return node.value
        elif isinstance(node.value, FunctionNode):
            func = self.process_function(node.value)
            return func
        elif isinstance(node.value, AliasNode):
            expr = self.process_alias(node.value)
            return expr
        else:
            raise CodeGenError("Unknown column node")

    def process_function(self, node):
        args = ", ".join(node.arguments)
        return f"{node.name.upper()}({args})"

    def process_alias(self, node):
            if isinstance(node.expression, FunctionNode):
                expr = self.process_function(node.expression)
            else:
                expr = node.expression
            
            alias = node.alias.strip('"').strip("'")
            if ' ' in alias:
                raise CodeGenError(f"Invalid alias name '{alias}'. Alias names cannot contain spaces.", node)
                
            return f"{expr} AS {alias}"

    def process_from(self, node):
        tables = ", ".join(node.tables)
        return "FROM " + tables

    def process_where(self, node):
        condition = self.process_condition(node.condition)
        return "WHERE " + condition

    def process_condition(self, node):
        if isinstance(node, ComparisonNode):
            left = self.process_operand(node.left)
            right = self.process_operand(node.right, wrap_strings=True)
            operator = self.get_operator(node.operator)
            return f"{left} {operator} {right}"
        elif isinstance(node, LogicalNode):
            left = self.process_condition(node.left)
            right = self.process_condition(node.right)
            operator = node.operator.upper()
            return f"({left} {operator} {right})"
        elif isinstance(node, BracketNode):
            expr = self.process_condition(node.expression)
            return f"({expr})"
        else:
            raise CodeGenError("Unknown condition node")

    def process_operand(self, operand, wrap_strings=False):
        if isinstance(operand, TableColumnRef):
            return f"{operand.table}.{operand.column}"
        elif isinstance(operand, FunctionNode):
            return self.process_function(operand)
        elif isinstance(operand, str):
            # Remove any existing quotes first
            cleaned = operand.strip('"').strip("'")
            # Only wrap in single quotes if it's meant to be a string constant
            return f"'{cleaned}'" if wrap_strings else cleaned
        elif isinstance(operand, int):
            return str(operand)
        else:
            raise CodeGenError("Unknown operand type")

    def get_operator(self, operator):
        operators = {
            "eq": "=",
            "gt": ">",
            "lt": "<",
            "ge": ">=",
            "le": "<=",
            "ne": "!=",
        }
        return operators.get(operator, operator)

    def process_group_by(self, node):
        columns = ", ".join(node.columns)
        return "GROUP BY " + columns

    def process_having(self, node):
        condition = self.process_condition(node.condition)
        return "HAVING " + condition

    def process_order_by(self, node):
        return f"ORDER BY {node.column} {node.direction.upper()}"


def generate_sql_from_ast(ast):
    generator = CodeGenerator(ast)
    sql_query = generator.generate()
    return sql_query


class CodeGenError(Exception):
    """Exception raised during code generation"""
    def __init__(self, message, node=None):
        self.node = node
        self.message = message
        if node:
            self.message += f" (Node type: {type(node).__name__})"
        super().__init__(self.message)

@dataclass
class QueryNode:
    select: 'SelectNode'
    from_: 'FromNode'
    where: Optional['WhereNode'] = None
    group_by: Optional['GroupByNode'] = None
    having: Optional['HavingNode'] = None
    order_by: Optional['OrderByNode'] = None

@dataclass
class SelectNode:
    columns: List['ColumnNode']

@dataclass
class ColumnNode:
    value: Union[str, 'FunctionNode', 'AliasNode']

@dataclass
class FunctionNode:
    name: str
    arguments: List[str]

@dataclass
class AliasNode:
    expression: Union[str, 'FunctionNode']
    alias: str

@dataclass
class FromNode:
    tables: List[str]

@dataclass
class WhereNode:
    condition: Union['ComparisonNode', 'LogicalNode', 'BracketNode']

@dataclass
class ComparisonNode:
    operator: str
    left: Union[str, 'TableColumnRef', 'FunctionNode']
    right: Union[str, int]

@dataclass
class TableColumnRef:
    table: str
    column: str

@dataclass
class LogicalNode:
    operator: str
    left: Union['ComparisonNode', 'BracketNode']
    right: Union['ComparisonNode', 'BracketNode', 'LogicalNode']

@dataclass
class BracketNode:
    expression: Union['ComparisonNode', 'LogicalNode']

@dataclass
class GroupByNode:
    columns: List[str]

@dataclass
class HavingNode:
    condition: 'ComparisonNode'

@dataclass
class OrderByNode:
    column: str
    direction: str

class TokenType(Enum):
    QUERY_OPEN = 1
    QUERY_CLOSE = 2
    SELECT_OPEN = 3
    SELECT_CLOSE = 4
    COLUMN_OPEN = 5
    COLUMN_CLOSE = 6
    COUNT_FUNC_OPEN = 7
    COUNT_FUNC_CLOSE = 8
    MAX_FUNC_OPEN = 9
    MAX_FUNC_CLOSE = 10
    ALIAS_OPEN = 11
    ALIAS_CLOSE = 12
    LHS_OPEN = 13
    LHS_CLOSE = 14
    RHS_OPEN = 15
    RHS_CLOSE = 16
    FROM_OPEN = 17
    FROM_CLOSE = 18
    TABLE_OPEN = 19
    TABLE_CLOSE = 20
    WHERE_OPEN = 21
    WHERE_CLOSE = 22
    EQ_OP_OPEN = 23
    EQ_OP_CLOSE = 24
    REF_TABLE_OPEN = 25
    REF_TABLE_CLOSE = 26
    REF_COL_OPEN = 27
    REF_COL_CLOSE = 28
    CONSTANT_OPEN = 29
    CONSTANT_CLOSE = 30
    STRING_CONSTANT_OPEN = 31
    STRING_CONSTANT_CLOSE = 32
    GROUP_BY_OPEN = 33
    GROUP_BY_CLOSE = 34
    HAVING_OPEN = 35
    HAVING_CLOSE = 36
    GT_OP_OPEN = 37
    GT_OP_CLOSE = 38
    INT_CONSTANT_OPEN = 39
    INT_CONSTANT_CLOSE = 40
    ORDER_BY_OPEN = 41
    ORDER_BY_CLOSE = 42
    DESC_OPEN = 43
    DESC_CLOSE = 44
    ASC_OPEN = 45
    ASC_CLOSE = 46
    BRACKET_OPEN = 47
    BRACKET_CLOSE = 48
    AND = 49
    OR = 50
    STRING_LITERAL = 51
    INT_LITERAL = 52
    COMMENT = 53

@dataclass
class Token:
    type: TokenType
    value: str

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        
    def parse(self) -> QueryNode:
        if self.match(TokenType.QUERY_OPEN):
            query = self.parse_query()
            if self.match(TokenType.QUERY_CLOSE):
                return query
        raise SyntaxError("Invalid query structure")

    def parse_query(self) -> QueryNode:
        select_node = self.parse_select()
        from_node = self.parse_from()
        where_node = self.parse_where() if self.peek().type == TokenType.WHERE_OPEN else None
        group_by_node = self.parse_group_by() if self.peek().type == TokenType.GROUP_BY_OPEN else None
        having_node = self.parse_having() if self.peek().type == TokenType.HAVING_OPEN else None
        order_by_node = self.parse_order_by() if self.peek().type == TokenType.ORDER_BY_OPEN else None
        
        return QueryNode(
            select=select_node,
            from_=from_node,
            where=where_node,
            group_by=group_by_node,
            having=having_node,
            order_by=order_by_node
        )

    def parse_select(self) -> SelectNode:
        if not self.match(TokenType.SELECT_OPEN):
            raise SyntaxError("Expected SELECT clause")
        
        columns = []
        while self.peek().type == TokenType.COLUMN_OPEN:
            columns.append(self.parse_column())
            
        if not self.match(TokenType.SELECT_CLOSE):
            raise SyntaxError("Unclosed SELECT clause")
            
        return SelectNode(columns)

    def parse_column(self) -> ColumnNode:
        if not self.match(TokenType.COLUMN_OPEN):
            raise SyntaxError("Expected column")
            
        value = None
        if self.peek().type == TokenType.STRING_LITERAL:
            value = self.consume().value
        elif self.peek().type in [TokenType.COUNT_FUNC_OPEN, TokenType.MAX_FUNC_OPEN]:
            value = self.parse_function()
        elif self.peek().type == TokenType.ALIAS_OPEN:
            value = self.parse_alias()
        else:
            raise SyntaxError("Invalid column content")
            
        if not self.match(TokenType.COLUMN_CLOSE):
            raise SyntaxError("Unclosed column")
            
        return ColumnNode(value)

    def parse_function(self) -> FunctionNode:
        func_type = self.peek().type
        if func_type == TokenType.COUNT_FUNC_OPEN:
            self.consume()
            name = "count"
        elif func_type == TokenType.MAX_FUNC_OPEN:
            self.consume()
            name = "max"
        else:
            raise SyntaxError("Expected function")
            
        # Collect all arguments
        args = []
        
        # Handle both direct string literals and column-wrapped arguments
        if self.peek().type == TokenType.STRING_LITERAL:
            args.append(self.consume().value)
        else:
            while self.peek().type == TokenType.COLUMN_OPEN:
                self.consume()  # consume COLUMN_OPEN
                if self.peek().type != TokenType.STRING_LITERAL:
                    raise SyntaxError("Expected column content")
                args.append(self.consume().value)
                if not self.match(TokenType.COLUMN_CLOSE):
                    raise SyntaxError("Unclosed column in function argument")
                
        if not args:
            raise SyntaxError("Expected at least one function argument")
            
        if not self.match(TokenType.COUNT_FUNC_CLOSE if name == "count" else TokenType.MAX_FUNC_CLOSE):
            raise SyntaxError("Unclosed function")
            
        return FunctionNode(name, args)
    def parse_alias(self) -> AliasNode:
        if not self.match(TokenType.ALIAS_OPEN):
            raise SyntaxError("Expected alias")
            
        if not self.match(TokenType.LHS_OPEN):
            raise SyntaxError("Expected alias LHS")
            
        expr = None
        if self.peek().type == TokenType.STRING_LITERAL:
            expr = self.consume().value
        elif self.peek().type in [TokenType.COUNT_FUNC_OPEN, TokenType.MAX_FUNC_OPEN]:
            expr = self.parse_function()
        else:
            raise SyntaxError("Invalid alias expression")
            
        if not self.match(TokenType.LHS_CLOSE):
            raise SyntaxError("Unclosed alias LHS")
            
        if not self.match(TokenType.RHS_OPEN):
            raise SyntaxError("Expected alias RHS")
            
        if self.peek().type != TokenType.STRING_LITERAL:
            raise SyntaxError("Expected alias name")
            
        alias = self.consume().value
        
        if not self.match(TokenType.RHS_CLOSE):
            raise SyntaxError("Unclosed alias RHS")
            
        if not self.match(TokenType.ALIAS_CLOSE):
            raise SyntaxError("Unclosed alias")
            
        return AliasNode(expr, alias)

    def parse_from(self) -> FromNode:
        if not self.match(TokenType.FROM_OPEN):
            raise SyntaxError("Expected FROM clause")
            
        tables = []
        # First token after FROM_OPEN must be TABLE_OPEN
        if self.peek().type == TokenType.STRING_LITERAL:
            raise SyntaxError("Table must be wrapped in <table> tags")
        
        while self.peek().type == TokenType.TABLE_OPEN:
            self.consume()
            if self.peek().type != TokenType.STRING_LITERAL:
                raise SyntaxError("Expected table name")
            tables.append(self.consume().value)
            if not self.match(TokenType.TABLE_CLOSE):
                raise SyntaxError("Unclosed table")
                
        if not self.match(TokenType.FROM_CLOSE):
            raise SyntaxError("Unclosed FROM clause")
            
        return FromNode(tables)

    def parse_where(self) -> WhereNode:
        if not self.match(TokenType.WHERE_OPEN):
            raise SyntaxError("Expected WHERE clause")
            
        condition = self.parse_condition()
            
        if not self.match(TokenType.WHERE_CLOSE):
            raise SyntaxError("Unclosed WHERE clause")
            
        return WhereNode(condition)

    def parse_condition(self) -> Union[ComparisonNode, LogicalNode, BracketNode]:
        if self.peek().type == TokenType.BRACKET_OPEN:
            return self.parse_bracket()
        elif self.peek().type in [TokenType.EQ_OP_OPEN, TokenType.GT_OP_OPEN]:
            condition = self.parse_comparison()
            if self.peek().type in [TokenType.AND, TokenType.OR]:
                op = "and" if self.peek().type == TokenType.AND else "or"
                self.consume()
                right = self.parse_condition()
                return LogicalNode(op, condition, right)
            return condition
        else:
            raise SyntaxError(f"Expected condition, got {self.peek().type}")

    def parse_comparison(self) -> ComparisonNode:
        op_type = self.peek().type
        if op_type not in [TokenType.EQ_OP_OPEN, TokenType.GT_OP_OPEN]:
            raise SyntaxError("Expected comparison operator")
            
        self.consume()
        operator = "eq" if op_type == TokenType.EQ_OP_OPEN else "gt"
        
        if not self.match(TokenType.LHS_OPEN):
            raise SyntaxError("Expected comparison LHS")
            
        left = self.parse_ref_or_value()
            
        if not self.match(TokenType.LHS_CLOSE):
            raise SyntaxError("Unclosed comparison LHS")
            
        if not self.match(TokenType.RHS_OPEN):
            raise SyntaxError("Expected comparison RHS")
            
        right = self.parse_constant()
            
        if not self.match(TokenType.RHS_CLOSE):
            raise SyntaxError("Unclosed comparison RHS")
            
        if not self.match(TokenType.EQ_OP_CLOSE if operator == "eq" else TokenType.GT_OP_CLOSE):
            raise SyntaxError("Unclosed comparison")
            
        return ComparisonNode(operator, left, right)

    def parse_ref_or_value(self) -> Union[str, TableColumnRef, FunctionNode]:
        if self.peek().type == TokenType.REF_TABLE_OPEN:
            # Parse table.column reference
            self.consume()
            if self.peek().type != TokenType.STRING_LITERAL:
                raise SyntaxError(f"Expected table name in <ref_table> tag")
            table = self.consume().value
            if not self.match(TokenType.REF_TABLE_CLOSE):
                raise SyntaxError("Unclosed table reference")
                
            if not self.match(TokenType.REF_COL_OPEN):
                raise SyntaxError("Expected <ref_col> after table reference")
            if self.peek().type != TokenType.STRING_LITERAL:
                raise SyntaxError("Expected column name in <ref_col> tag")
            column = self.consume().value
            if not self.match(TokenType.REF_COL_CLOSE):
                raise SyntaxError("Unclosed column reference")
                
            return TableColumnRef(table, column)
        elif self.peek().type == TokenType.STRING_LITERAL:
            value = self.consume().value
            return value
        elif self.peek().type in [TokenType.COUNT_FUNC_OPEN, TokenType.MAX_FUNC_OPEN]:
            return self.parse_function()
        else:
            raise SyntaxError(f"Expected either:\n" +
                            "1. Table and column reference (<ref_table>...<ref_col>)\n" +
                            "2. String literal\n" +
                            "3. Function call (count_func or max_func)\n" +
                            f"Got {self.peek().type} instead")
    
    def parse_constant(self) -> Union[str, int]:
        if self.peek().type == TokenType.STRING_CONSTANT_OPEN:
            self.consume()
            if self.peek().type != TokenType.STRING_LITERAL:
                raise SyntaxError("Expected string constant")
            value = self.consume().value
            if not self.match(TokenType.STRING_CONSTANT_CLOSE):
                raise SyntaxError("Unclosed string constant")
            return value
        elif self.peek().type == TokenType.INT_CONSTANT_OPEN:
            self.consume()
            if self.peek().type != TokenType.INT_LITERAL:
                raise SyntaxError("Expected integer constant")
            value = int(self.consume().value)
            if not self.match(TokenType.INT_CONSTANT_CLOSE):
                raise SyntaxError("Unclosed integer constant")
            return value
        else:
            raise SyntaxError("Expected constant")

    def parse_bracket(self) -> BracketNode:
        if not self.match(TokenType.BRACKET_OPEN):
            raise SyntaxError("Expected bracket expression")
            
        expr = self.parse_condition()
            
        if not self.match(TokenType.BRACKET_CLOSE):
            raise SyntaxError("Unclosed bracket expression")
            
        return BracketNode(expr)

    def parse_group_by(self) -> GroupByNode:
        if not self.match(TokenType.GROUP_BY_OPEN):
            raise SyntaxError("Expected GROUP BY clause")
            
        columns = []
        while self.peek().type == TokenType.COLUMN_OPEN:
            self.consume()
            if self.peek().type != TokenType.STRING_LITERAL:
                raise SyntaxError("Expected column name")
            columns.append(self.consume().value)
            if not self.match(TokenType.COLUMN_CLOSE):
                raise SyntaxError("Unclosed column")
                
        if not self.match(TokenType.GROUP_BY_CLOSE):
            raise SyntaxError("Unclosed GROUP BY clause")
            
        return GroupByNode(columns)

    def parse_having(self) -> HavingNode:
        if not self.match(TokenType.HAVING_OPEN):
            raise SyntaxError("Expected HAVING clause")
            
        condition = self.parse_condition()
            
        if not self.match(TokenType.HAVING_CLOSE):
            raise SyntaxError("Unclosed HAVING clause")
            
        return HavingNode(condition)
    
    def parse_order_by(self) -> OrderByNode:
        if not self.match(TokenType.ORDER_BY_OPEN):
            raise SyntaxError("Expected ORDER BY clause")
            
        direction = None
        column = None
        
        if self.peek().type == TokenType.ASC_OPEN:
            self.consume()
            direction = "asc"
        elif self.peek().type == TokenType.DESC_OPEN:
            self.consume()
            direction = "desc"
        else:
            raise SyntaxError("Expected sort direction")
            
        if not self.match(TokenType.REF_COL_OPEN):
            raise SyntaxError("Expected column reference")
        
        if self.peek().type != TokenType.STRING_LITERAL:
            raise SyntaxError("Expected column name")
        
        column = self.consume().value
        
        if not self.match(TokenType.REF_COL_CLOSE):
            raise SyntaxError("Unclosed column reference")
            
        if not self.match(TokenType.ASC_CLOSE if direction == "asc" else TokenType.DESC_CLOSE):
            raise SyntaxError("Unclosed sort direction")
            
        if not self.match(TokenType.ORDER_BY_CLOSE):
            raise SyntaxError("Unclosed ORDER BY clause")
            
        return OrderByNode(column, direction)

    def match(self, type: TokenType) -> bool:
        if self.peek().type == type:
            self.consume()
            return True
        return False
        
    def peek(self) -> Token:
        if self.current >= len(self.tokens):
            raise SyntaxError("Unexpected end of input")
        return self.tokens[self.current]
        
    def consume(self) -> Token:
        token = self.peek()
        self.current += 1
        return token

def parse_tokens_file(file_path: str) -> QueryNode:
    tokens = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
                
            # Extract type and value from format like <QUERY_OPEN, <query>>
            if line.startswith('<') and line.endswith('>'):
                # Remove outer < and >
                content = line[1:-1]
                # Split at first comma
                parts = content.split(', ', 1)
                if len(parts) == 2:
                    type_str = parts[0]  # This is like QUERY_OPEN
                    value = parts[1]     # This is like <query>
                    
                    # Remove any < or > from value
                    value = value.strip('<>')
                    
                    # Skip comments - don't add them to tokens
                    if type_str == 'COMMENT':
                        continue
                        
                    if type_str in TokenType.__members__:
                        tokens.append(Token(TokenType[type_str], value))
    
    if not tokens:
        raise ValueError("No valid tokens found in file")
        
    parser = Parser(tokens)
    return parser.parse()
"""
def print_ast(node, indent=0):
    prefix = "  " * indent
    
    if isinstance(node, QueryNode):
        print(f"{prefix}Query:")
        print_ast(node.select, indent + 1)
        print_ast(node.from_, indent + 1)
        if node.where:
            print_ast(node.where, indent + 1)
        if node.group_by:
            print_ast(node.group_by, indent + 1)
        if node.having:
            print_ast(node.having, indent + 1)
        if node.order_by:
            print_ast(node.order_by, indent + 1)
    
    elif isinstance(node, SelectNode):
        print(f"{prefix}Select:")
        for col in node.columns:
            print_ast(col, indent + 1)
    
    elif isinstance(node, ColumnNode):
        if isinstance(node.value, str):
            print(f"{prefix}Column: {node.value}")
        else:
            print(f"{prefix}Column:")
            print_ast(node.value, indent + 1)
    
    elif isinstance(node, FunctionNode):
        print(f"{prefix}Function {node.name}({node.argument})")
    
    elif isinstance(node, AliasNode):
        print(f"{prefix}Alias:")
        print(f"{prefix}  Expression:")
        if isinstance(node.expression, str):
            print(f"{prefix}    {node.expression}")
        else:
            print_ast(node.expression, indent + 2)
        print(f"{prefix}  As: {node.alias}")
    
    elif isinstance(node, FromNode):
        print(f"{prefix}From:")
        for table in node.tables:
            print(f"{prefix}  Table: {table}")
    
    elif isinstance(node, WhereNode):
        print(f"{prefix}Where:")
        print_ast(node.condition, indent + 1)
    
    elif isinstance(node, ComparisonNode):
        print(f"{prefix}Comparison ({node.operator}):")
        print(f"{prefix}  Left:")
        if isinstance(node.left, str):
            print(f"{prefix}    {node.left}")
        else:
            print_ast(node.left, indent + 2)
        print(f"{prefix}  Right: {node.right}")
    
    elif isinstance(node, TableColumnRef):
        print(f"{prefix}Reference: {node.table}.{node.column}")
    
    elif isinstance(node, LogicalNode):
        print(f"{prefix}Logical {node.operator}:")
        print(f"{prefix}  Left:")
        print_ast(node.left, indent + 2)
        print(f"{prefix}  Right:")
        print_ast(node.right, indent + 2)
    
    elif isinstance(node, BracketNode):
        print(f"{prefix}Bracketed Expression:")
        print_ast(node.expression, indent + 1)
    
    elif isinstance(node, GroupByNode):
        print(f"{prefix}Group By:")
        for col in node.columns:
            print(f"{prefix}  Column: {col}")
    
    elif isinstance(node, HavingNode):
        print(f"{prefix}Having:")
        print_ast(node.condition, indent + 1)
    
    elif isinstance(node, OrderByNode):
        print(f"{prefix}Order By:")
        print(f"{prefix}  Column: {node.column}")
        print(f"{prefix}  Direction: {node.direction}")
"""
"""
def process_lexer_output():
    output_dir = "./lexer_output"
    if not os.path.exists(output_dir):
        print(f"Error: Directory {output_dir} does not exist")
        return
    
    for filename in os.listdir(output_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(output_dir, filename)
            print(f"\nProcessing {filename}:")
            try:
                ast = parse_tokens_file(file_path)
                print("Successfully parsed. AST structure:")
                print_ast(ast)
            except Exception as e:
                print(f"Error parsing {filename}: {str(e)}")
"""
def process_files(input_dir: str = "./lexer_output", output_dir: str = "./parser_output", codegen_dir: str = "./codegen_output"):
    if not os.path.exists(input_dir):
        print(f"Error: Input directory {input_dir} does not exist")
        return
        
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(codegen_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_dir, filename)

            # extract original filename
            filename = filename.split('_')[1]

            output_path = os.path.join(output_dir, f"parsed_{filename}")

            codegen_path = os.path.join(codegen_dir, f"code_gen_{filename}")
            
            print(f"\nProcessing {filename}:")
            try:
                ast = parse_tokens_file(input_path)
                print("Successfully parsed. Check output file for AST structure.")
                # Write AST to output file
                with open(output_path, 'w') as f:
                    f.write("Successfully parsed. AST structure:\n")
                    write_ast_to_file(ast, f)
                
               
                try:
                    print("Starting SQL code generation...")
                    val = generate_sql_from_ast(ast)
                    print("Generated SQL:", val)
                    with open(codegen_path, 'w') as f:
                        f.write(val)
                    print("Code generation successful")
                except CodeGenError as e:
                    print(f"Code generation failed: {e.message}")
                    with open(codegen_path, 'w') as f:
                        f.write(f"Code Generation Error: {e.message}\n")
                    continue
                    
            except Exception as e:
                print(f"Error parsing {filename}: {str(e)}")
                # Write error to output file
                with open(output_path, 'w') as f:
                    f.write(f"Error parsing file: {str(e)}\n")

def write_ast_to_file(node, file, indent=0):
    prefix = "  " * indent
    
    if isinstance(node, QueryNode):
        file.write(f"{prefix}Query:\n")
        write_ast_to_file(node.select, file, indent + 1)
        write_ast_to_file(node.from_, file, indent + 1)
        if node.where:
            write_ast_to_file(node.where, file, indent + 1)
        if node.group_by:
            write_ast_to_file(node.group_by, file, indent + 1)
        if node.having:
            write_ast_to_file(node.having, file, indent + 1)
        if node.order_by:
            write_ast_to_file(node.order_by, file, indent + 1)
    
    elif isinstance(node, SelectNode):
        file.write(f"{prefix}Select:\n")
        for col in node.columns:
            write_ast_to_file(col, file, indent + 1)
    
    elif isinstance(node, ColumnNode):
        if isinstance(node.value, str):
            file.write(f"{prefix}Column: {node.value}\n")
        else:
            file.write(f"{prefix}Column:\n")
            write_ast_to_file(node.value, file, indent + 1)
    
    elif isinstance(node, FunctionNode):
        file.write(f"{prefix}Function: {node.name}\n")
        file.write(f"{prefix}  Parameters:\n")
        for arg in node.arguments:
            file.write(f"{prefix}    Column: {arg}\n")
    
    elif isinstance(node, AliasNode):
        file.write(f"{prefix}Alias:\n")
        file.write(f"{prefix}  Expression:\n")
        if isinstance(node.expression, str):
            file.write(f"{prefix}    {node.expression}\n")
        else:
            write_ast_to_file(node.expression, file, indent + 2)
        file.write(f"{prefix}  As: {node.alias}\n")
    
    elif isinstance(node, FromNode):
        file.write(f"{prefix}From:\n")
        for table in node.tables:
            file.write(f"{prefix}  Table: {table}\n")
    
    elif isinstance(node, WhereNode):
        file.write(f"{prefix}Where:\n")
        write_ast_to_file(node.condition, file, indent + 1)
    
    elif isinstance(node, ComparisonNode):
        file.write(f"{prefix}Comparison ({node.operator}):\n")
        file.write(f"{prefix}  Left:\n")
        if isinstance(node.left, str):
            file.write(f"{prefix}    {node.left}\n")
        else:
            write_ast_to_file(node.left, file, indent + 2)
        file.write(f"{prefix}  Right: {node.right}\n")
    
    elif isinstance(node, TableColumnRef):
        file.write(f"{prefix}Reference: {node.table}.{node.column}\n")
    
    elif isinstance(node, LogicalNode):
        file.write(f"{prefix}Logical {node.operator}:\n")
        file.write(f"{prefix}  Left:\n")
        write_ast_to_file(node.left, file, indent + 2)
        file.write(f"{prefix}  Right:\n")
        write_ast_to_file(node.right, file, indent + 2)
    
    elif isinstance(node, BracketNode):
        file.write(f"{prefix}Bracketed Expression:\n")
        write_ast_to_file(node.expression, file, indent + 1)
    
    elif isinstance(node, GroupByNode):
        file.write(f"{prefix}Group By:\n")
        for col in node.columns:
            file.write(f"{prefix}  Column: {col}\n")
    
    elif isinstance(node, HavingNode):
        file.write(f"{prefix}Having:\n")
        write_ast_to_file(node.condition, file, indent + 1)
    
    elif isinstance(node, OrderByNode):
        file.write(f"{prefix}Order By:\n")
        file.write(f"{prefix}  Column: {node.column}\n")
        file.write(f"{prefix}  Direction: {node.direction}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse XML SQL tokens into AST')
    parser.add_argument('--input', default='./lexer_output', 
                      help='Input directory containing lexer output files (default: ./lexer_output)')
    parser.add_argument('--output', default='./parser_output',
                      help='Output directory for parser results (default: ./parser_output)')
    
    args = parser.parse_args()
    process_files(args.input, args.output)
    
    print("\nParsing complete. Check the output directory for results.")
import enum
import os

class TokenType(enum.Enum):
    QUERY_OPEN, QUERY_CLOSE = 1, 2
    SELECT_OPEN, SELECT_CLOSE = 3, 4
    COLUMN_OPEN, COLUMN_CLOSE = 5, 6
    COUNT_FUNC_OPEN, COUNT_FUNC_CLOSE = 7, 8
    MAX_FUNC_OPEN, MAX_FUNC_CLOSE = 9, 10
    ALIAS_OPEN, ALIAS_CLOSE = 11, 12
    LHS_OPEN, LHS_CLOSE = 13, 14
    RHS_OPEN, RHS_CLOSE = 15, 16
    FROM_OPEN, FROM_CLOSE = 17, 18
    TABLE_OPEN, TABLE_CLOSE = 19, 20
    WHERE_OPEN, WHERE_CLOSE = 21, 22
    EQ_OP_OPEN, EQ_OP_CLOSE = 23, 24
    REF_TABLE_OPEN, REF_TABLE_CLOSE = 25, 26
    REF_COL_OPEN, REF_COL_CLOSE = 27, 28
    CONSTANT_OPEN, CONSTANT_CLOSE = 29, 30
    STRING_CONSTANT_OPEN, STRING_CONSTANT_CLOSE = 31, 32
    GROUP_BY_OPEN, GROUP_BY_CLOSE = 33, 34
    HAVING_OPEN, HAVING_CLOSE = 35, 36
    GT_OP_OPEN, GT_OP_CLOSE = 37, 38
    INT_CONSTANT_OPEN, INT_CONSTANT_CLOSE = 39, 40
    ORDER_BY_OPEN, ORDER_BY_CLOSE = 41, 42
    DESC_OPEN, DESC_CLOSE = 43, 44
    ASC_OPEN, ASC_CLOSE = 45, 46
    BRACKET_OPEN, BRACKET_CLOSE = 47, 48
    
    AND, OR = 49, 50
    
    STRING_LITERAL, INT_LITERAL = 51, 52

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"<{self.type.name}, {self.value}>"

class Scanner:
    def __init__(self, input_text):
        self.input = input_text
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.self_closing_tags = {"and", "or"}
    
    def advance(self):
        if self.position < len(self.input):
            if self.input[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def scan(self):
        while self.position < len(self.input):
            if self.input[self.position].isspace():
                self.advance()
            elif self.input[self.position] == '<':
                self.scan_tag()
            elif self.input[self.position] in ['"', "'"]:
                self.scan_string_literal()
            elif self.input[self.position].isdigit():
                self.scan_int_literal()
            else:
                self.error(f"Unexpected character: {self.input[self.position]}")

        return self.tokens


    def scan_tag(self):
        """
        if self.is_unclosed_string_literal():
            self.error("Unclosed string literal before tag")
        """

        start = self.position
        start_line, start_column = self.line, self.column
        self.advance()  
        is_closing = False
        if self.position < len(self.input) and self.input[self.position] == '/':
            is_closing = True
            self.advance()

        tag_name = ""
        while self.position < len(self.input) and self.input[self.position] not in ('>', '/', ' '):
            tag_name += self.input[self.position]
            self.advance()

        tag_name = tag_name.strip()

        if self.position < len(self.input):
            if self.input[self.position] == '/':
                self.advance()
                if self.position < len(self.input) and self.input[self.position] == '>':
                    self.advance()
                    self.add_tag_token(tag_name, is_self_closing=True)
                else:
                    self.error(f"Invalid self-closing tag", start_line, start_column)
            elif self.input[self.position] == '>':
                self.advance()
                self.add_tag_token(tag_name, is_closing=is_closing)
            else:
                self.error(f"Invalid tag", start_line, start_column)
        else:
            self.error("Unclosed tag", start_line, start_column)

    def add_tag_token(self, tag_name, is_closing=False, is_self_closing=False):
        tag_type_map = {
            "query": (TokenType.QUERY_OPEN, TokenType.QUERY_CLOSE),
            "select": (TokenType.SELECT_OPEN, TokenType.SELECT_CLOSE),
            "column": (TokenType.COLUMN_OPEN, TokenType.COLUMN_CLOSE),
            "count_func": (TokenType.COUNT_FUNC_OPEN, TokenType.COUNT_FUNC_CLOSE),
            "max_func": (TokenType.MAX_FUNC_OPEN, TokenType.MAX_FUNC_CLOSE),
            "alias": (TokenType.ALIAS_OPEN, TokenType.ALIAS_CLOSE),
            "lhs": (TokenType.LHS_OPEN, TokenType.LHS_CLOSE),
            "rhs": (TokenType.RHS_OPEN, TokenType.RHS_CLOSE),
            "from": (TokenType.FROM_OPEN, TokenType.FROM_CLOSE),
            "table": (TokenType.TABLE_OPEN, TokenType.TABLE_CLOSE),
            "where": (TokenType.WHERE_OPEN, TokenType.WHERE_CLOSE),
            "eq_op": (TokenType.EQ_OP_OPEN, TokenType.EQ_OP_CLOSE),
            "ref_table": (TokenType.REF_TABLE_OPEN, TokenType.REF_TABLE_CLOSE),
            "ref_col": (TokenType.REF_COL_OPEN, TokenType.REF_COL_CLOSE),
            "constant": (TokenType.CONSTANT_OPEN, TokenType.CONSTANT_CLOSE),
            "string_constant": (TokenType.STRING_CONSTANT_OPEN, TokenType.STRING_CONSTANT_CLOSE),
            "group_by": (TokenType.GROUP_BY_OPEN, TokenType.GROUP_BY_CLOSE),
            "having": (TokenType.HAVING_OPEN, TokenType.HAVING_CLOSE),
            "gt_op": (TokenType.GT_OP_OPEN, TokenType.GT_OP_CLOSE),
            "int_constant": (TokenType.INT_CONSTANT_OPEN, TokenType.INT_CONSTANT_CLOSE),
            "order_by": (TokenType.ORDER_BY_OPEN, TokenType.ORDER_BY_CLOSE),
            "desc": (TokenType.DESC_OPEN, TokenType.DESC_CLOSE),
            "asc": (TokenType.ASC_OPEN, TokenType.ASC_CLOSE),
            "bracket": (TokenType.BRACKET_OPEN, TokenType.BRACKET_CLOSE),
        }

        if tag_name in self.self_closing_tags:
            if not is_self_closing:
                self.error(f"Tag <{tag_name}> must be self-closing")
            self.tokens.append(Token(TokenType[tag_name.upper()], f"<{tag_name}/>"))
        elif is_self_closing:
            if tag_name in tag_type_map:
                self.tokens.append(Token(tag_type_map[tag_name][0], f"<{tag_name}/>"))
            else:
                self.error(f"Unknown self-closing tag: <{tag_name}/>")
        else:
            if tag_name in tag_type_map:
                token_type = tag_type_map[tag_name][1 if is_closing else 0]
                self.tokens.append(Token(token_type, f"<{'/' if is_closing else ''}{tag_name}>"))
            else:
                self.error(f"Unknown tag: <{'/' if is_closing else ''}{tag_name}>")




    def scan_int_literal(self):
        start = self.position
        while self.position < len(self.input) and self.input[self.position].isdigit():
            self.advance()
        self.tokens.append(Token(TokenType.INT_LITERAL, self.input[start:self.position]))

    def scan_string_literal(self):
        start = self.position
        start_line, start_column = self.line, self.column
        quote_char = self.input[self.position]
        self.advance()
        while self.position < len(self.input) and self.input[self.position] != quote_char:
            self.advance()
        if self.position < len(self.input):
            self.advance()  
            value = self.input[start+1:self.position-1]
            self.tokens.append(Token(TokenType.STRING_LITERAL, value))
        else:
            self.error("Unclosed string literal", start_line, start_column)
    """
    def is_unclosed_string_literal(self):
        current_pos = self.position
        
        while current_pos < len(self.input) and self.input[current_pos].isspace():
            current_pos += 1
        
        if current_pos < len(self.input) and self.input[current_pos] in ['"', "'"]:
            quote_char = self.input[current_pos]
            current_pos += 1
            while current_pos < len(self.input) and self.input[current_pos] != quote_char:s
                current_pos += 1
            if current_pos == len(self.input):
                return True  
        
        return False
    """
    
 
    def error(self, message, line=None, column=None):
        if line is None:
            line = self.line
        if column is None:
            column = self.column
        raise ValueError(f"Error at line {line}, column {column}: {message}")

def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            input_text = file.read()
        
        scanner = Scanner(input_text)
        tokens = scanner.scan()
        print("\n\n\n\n")
        
        print(f"Successfully processed {file_path}")
        print("Tokens:")
        for token in tokens:
            print(token)
        print("\n\n\n\n")
    except ValueError as e:
        print("\n\n\n\n")
        print(f"Error in file {file_path}: {str(e)}")
        print("\n\n\n\n")
    except Exception as e:
        print("\n\n\n\n\n")
        print(f"Unexpected error in file {file_path}: {str(e)}")
        print("\n\n\n\n")


def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".xml") or filename.endswith(".txt"):  
            file_path = os.path.join(folder_path, filename)
            process_file(file_path)

if __name__ == "__main__":
    folder_path = "./tests/"  
    process_folder(folder_path)
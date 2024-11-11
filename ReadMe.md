# COMS W4115

## Lexical Grammar

The language is an xml based representation of sql code.
 
For instance ./tests/test1.xml when translated to sql looks as follows :
```
 select class, count(*), max(stats) as max_stats
 from characters,games
 where games.game='genshin' and (games.origin='USA' or games.origin='JAPAN')
 group by class having count(*)>3
 order by class asc
```

We have the following Class of tokens :

1)Tokens with opening tags :
- Generalized Structure Regex : `<[a-zA-Z][a-zA-Z0-9]*>`
- This includes tags like `<select>, <from>, <where>`, etc
- Pattern Matching Rule :
  - '<' is scanned
  - the following character is not "/"
  - ends with '>' before encountering a '/'
   - Returns Corresponding Token if content of the text between '<' and '>' is one among the following strings:
 [query, select, column, count_func, max_func, alias, lhs, rhs, from, table, where, eq_op, ref_table, ref_col, constant, string_constant, group_by, having, gt_op, int_constant, order_by, desc, asc, bracket].

  - Corresponding Tokens Returned : 
  `QUERY_OPEN, SELECT_OPEN, COLUMN_OPEN, COUNT_FUNC_OPEN, MAX_FUNC_OPEN, ALIAS_OPEN, LHS_OPEN, RHS_OPEN, FROM_OPEN, TABLE_OPEN, WHERE_OPEN, EQ_OP_OPEN, REF_TABLE_OPEN, REF_COL_OPEN, CONSTANT_OPEN, STRING_CONSTANT_OPEN, GROUP_BY_OPEN, HAVING_OPEN, GT_OP_OPEN, INT_CONSTANT_OPEN, ORDER_BY_OPEN, DESC_OPEN, ASC_OPEN, BRACKET_OPEN`.



2)Tokens with closing tags :
- Generalized Structure Regex : `</[a-zA-Z][a-zA-Z0-9]*>`
- This includes tags like `</select>, </from>, </where>`, etc
- Pattern Matching Rule :
  - '<' is scanned
  - the following character is "/"
  - ends with '>' before encountering a '/'
- Returns Corresponding Token if content of the text between '<' and '/>' is one among the following strings:
 [query, select, column, count_func, max_func, alias, lhs, rhs, from, table, where, eq_op, ref_table, ref_col, constant, string_constant, group_by, having, gt_op, int_constant, order_by, desc, asc, bracket].
- Corresponding Tokens Returned : 
  `QUERY_CLOSE, SELECT_CLOSE, COLUMN_CLOSE, COUNT_FUNC_CLOSE, MAX_FUNC_CLOSE, ALIAS_CLOSE, LHS_CLOSE, RHS_CLOSE, FROM_CLOSE, TABLE_CLOSE, WHERE_CLOSE, EQ_OP_CLOSE, REF_TABLE_CLOSE, REF_COL_CLOSE, CONSTANT_CLOSE, STRING_CONSTANT_CLOSE, GROUP_BY_CLOSE, HAVING_CLOSE, GT_OP_CLOSE, INT_CONSTANT_CLOSE, ORDER_BY_CLOSE, DESC_CLOSE, ASC_CLOSE, BRACKET_CLOSE.`
  

3)Tokens with self-closing tags :
- Generalized Structure Regex : `<[a-zA-Z][a-zA-Z0-9]*/>`
- This includes tags like `<and/>,<or/>` etc
- Pattern Matching Rule :
  - '<' is scanned
  - the following character is not "/"
  - ends with '/' before encountering a '>'
- Returns Corresponding Token if content of the text between '<' and '/>' is one among the following strings:
 [AND, OR].
- Corresponding Tokens Returned : 
  `AND, OR`
 


4)String :
- Regex : `"[^"]*"` or `'[^']*'` where in ^ represents negation. i.e. `[^"]` => all characters except `"`
- This includes strings enclosed within double or single quotes
- This includes  strings like "PROJECT", 'HOMEWORK', etc
- Corresponding Token Returned `STRING_LITERAL`

5)Numbers :
- Regex : `[0-9]+`
- Consists of Sequence of digits 
- This includes numbers like 123,0 etc
- Corresponding Token Returned `INTEGER_LITERAL`

6)Comments :
- Regex : `<!--[a-zA-Z0-9]*-->`
- This includes any string or number enclosed by `<!--` and `-->`
- Corresponding Token Returned `COMMENT`

## TESTS

- The .xml files to be tested can be found under ./tests directory 
- test1.xml doesn't have any errors , Expected Output :
```
Successfully processed ./tests/test1.xml
Tokens:
<QUERY_OPEN, <query>>
<SELECT_OPEN, <select>>
<COLUMN_OPEN, <column>>
<STRING_LITERAL, class>
<COLUMN_CLOSE, </column>>
<COLUMN_OPEN, <column>>
<COUNT_FUNC_OPEN, <count_func>>
<STRING_LITERAL, *>
<COUNT_FUNC_CLOSE, </count_func>>
<COLUMN_CLOSE, </column>>
<COLUMN_OPEN, <column>>
<ALIAS_OPEN, <alias>>
<LHS_OPEN, <lhs>>
<MAX_FUNC_OPEN, <max_func>>
<STRING_LITERAL, stats>
<MAX_FUNC_CLOSE, </max_func>>
<LHS_CLOSE, </lhs>>
<RHS_OPEN, <rhs>>
<STRING_LITERAL, max_stats>
<RHS_CLOSE, </rhs>>
<ALIAS_CLOSE, </alias>>
<COLUMN_CLOSE, </column>>
<SELECT_CLOSE, </select>>
<FROM_OPEN, <from>>
<TABLE_OPEN, <table>>
<STRING_LITERAL, characters>
<TABLE_CLOSE, </table>>
<TABLE_OPEN, <table>>
<STRING_LITERAL, games>
<TABLE_CLOSE, </table>>
<FROM_CLOSE, </from>>
<WHERE_OPEN, <where>>
<EQ_OP_OPEN, <eq_op>>
<LHS_OPEN, <lhs>>
<REF_TABLE_OPEN, <ref_table>>
<STRING_LITERAL, games>
<REF_TABLE_CLOSE, </ref_table>>
<REF_COL_OPEN, <ref_col>>
<STRING_LITERAL, game>
<REF_COL_CLOSE, </ref_col>>
<LHS_CLOSE, </lhs>>
<RHS_OPEN, <rhs>>
<STRING_CONSTANT_OPEN, <string_constant>>
<STRING_LITERAL, 'genshin'>
<STRING_CONSTANT_CLOSE, </string_constant>>
<RHS_CLOSE, </rhs>>
<EQ_OP_CLOSE, </eq_op>>
<AND, <and/>>
<BRACKET_OPEN, <bracket>>
<EQ_OP_OPEN, <eq_op>>
<LHS_OPEN, <lhs>>
<REF_TABLE_OPEN, <ref_table>>
<STRING_LITERAL, games>
<REF_TABLE_CLOSE, </ref_table>>
<REF_COL_OPEN, <ref_col>>
<STRING_LITERAL, origin>
<REF_COL_CLOSE, </ref_col>>
<LHS_CLOSE, </lhs>>
<RHS_OPEN, <rhs>>
<STRING_CONSTANT_OPEN, <string_constant>>
<STRING_LITERAL, 'USA'>
<STRING_CONSTANT_CLOSE, </string_constant>>
<RHS_CLOSE, </rhs>>
<EQ_OP_CLOSE, </eq_op>>
<OR, <or/>>
<EQ_OP_OPEN, <eq_op>>
<LHS_OPEN, <lhs>>
<REF_TABLE_OPEN, <ref_table>>
<STRING_LITERAL, games>
<REF_TABLE_CLOSE, </ref_table>>
<REF_COL_OPEN, <ref_col>>
<STRING_LITERAL, origin>
<REF_COL_CLOSE, </ref_col>>
<LHS_CLOSE, </lhs>>
<RHS_OPEN, <rhs>>
<STRING_CONSTANT_OPEN, <string_constant>>
<STRING_LITERAL, 'Japan'>
<STRING_CONSTANT_CLOSE, </string_constant>>
<RHS_CLOSE, </rhs>>
<EQ_OP_CLOSE, </eq_op>>
<BRACKET_CLOSE, </bracket>>
<WHERE_CLOSE, </where>>
<GROUP_BY_OPEN, <group_by>>
<COLUMN_OPEN, <column>>
<STRING_LITERAL, class>
<COLUMN_CLOSE, </column>>
<GROUP_BY_CLOSE, </group_by>>
<HAVING_OPEN, <having>>
<GT_OP_OPEN, <gt_op>>
<LHS_OPEN, <lhs>>
<COUNT_FUNC_OPEN, <count_func>>
<COLUMN_OPEN, <column>>
<STRING_LITERAL, *>
<COLUMN_CLOSE, </column>>
<COUNT_FUNC_CLOSE, </count_func>>
<LHS_CLOSE, </lhs>>
<RHS_OPEN, <rhs>>
<INT_CONSTANT_OPEN, <int_constant>>
<INT_LITERAL, 3>
<INT_CONSTANT_CLOSE, </int_constant>>
<RHS_CLOSE, </rhs>>
<GT_OP_CLOSE, </gt_op>>
<HAVING_CLOSE, </having>>
<ORDER_BY_OPEN, <order_by>>
<ASC_OPEN, <asc>>
<REF_COL_OPEN, <ref_col>>
<STRING_LITERAL, class>
<REF_COL_CLOSE, </ref_col>>
<ASC_CLOSE, </asc>>
<ORDER_BY_CLOSE, </order_by>>
<QUERY_CLOSE, </query>>
```
- test2.xml uses `<tab>` `</tab>` but no such tag exists , we only have `<table>` and `</table>`
```
Error in file ./tests/test2.xml: Error at line 7, column 12: Unknown tag: <tab>
```
- test3.xml has or tag that is not properly closed : `<or` instead of `<or\>`
```
Error in file ./tests/test3.xml: Error at line 18, column 13: Invalid tag
```
- test4.xml has a string that is not properly closed `"1` instead of `"1"` 
Expected output :
```
Error in file ./tests/test4.xml: Error at line 4, column 15: Unclosed string literal
```
- test5.xml forgets to enclose `*` within quotes, it should be `"*"`
```
Error in file ./tests/test5.xml: Error at line 4, column 15: Unexpected character: *
```
- test6.xml doesn't have any errors, Expected Output:
```
Successfully processed ./tests/test6.xml
Tokens:
<QUERY_OPEN, <query>>
<SELECT_OPEN, <select>>
<COLUMN_OPEN, <column>>
<STRING_LITERAL, *>
<COLUMN_CLOSE, </column>>
<SELECT_CLOSE, </select>>
<FROM_OPEN, <from>>
<TABLE_OPEN, <table>>
<STRING_LITERAL, table>
<TABLE_CLOSE, </table>>
<FROM_CLOSE, </from>>
<QUERY_CLOSE, </query>>
<COMMENT, adasd>
```

## Parser
The parser reads the output file of the tokenizer and match each token to a data class defined in the parser, then link them up to form an AST for parsing. It will check the corresponding errors (i.e. unclosed clauses, missing arguments) for each token.

Context Free Grammar for all the tokens:
- Select → SELECT_OPEN ColumnList SELECT_CLOSE
- ColumnList → Column | Column ColumnList
- Column → COLUMN_OPEN Column_Inner  COLUMN_CLOSE
- Column_Inner → STRING_LITERAL | Function | Alias
- From → FROM_OPEN TableList FROM_CLOSE
- TableList → Table | Table TableList
- Table → TABLE_OPEN STRING_LITERAL TABLE_CLOSE
- Query → QUERY_OPEN Select From Query_Inner QUERY_CLOSE
- Query_Inner → Where_opt GroupBy_opt Having_opt OrderBy_opt
- Where_opt → Where | ε
- GroupBy_opt → GroupBy | ε
- Having_opt → Having | ε
- OrderBy_opt → OrderBy | ε
- Function → COUNT_FUNC_OPEN Func_Inner COUNT_FUNC_CLOSE | MAX_FUNC_OPEN Func_Inner MAX_FUNC_CLOSE
- Function_Inner → STRING_LITERAL | Column_Args
- Column_Args → COLUMN_OPEN STRING_LITERAL COLUMN_CLOSE | COLUMN_OPEN STRING_LITERAL COLUMN_CLOSE Column_Args
- Alias → ALIAS_OPEN LHS_OPEN Alias_Inner LHS_CLOSE RHS_OPEN STRING_LITERAL RHS_CLOSE ALIAS_CLOSE
- Alias_Inner → STRING_LITERAL | Function
- Where → WHERE_OPEN condition WHERE_CLOSE
- Condition → Bracket | Comparison | Logical_Expression
- Logical_Expression → Comparison AND Condition | Comparison OR Condition
- Bracket → BRACKET_OPEN Condition BRACKET_CLOSE
- Comparison → EQ_OP_OPEN Comparison_Inner EQ_OP_CLOSE | GT_OP_OPEN Comparison_Inner GT_OP_CLOSE
- Comparison_Inner → LHS_OPEN Ref_or_Value LHS_CLOSE RHS_OPEN Constant RHS_CLOSE
- Ref_or_Value → Table_Column_Ref | STRING_LITERAL | Function
- Table_Column_Ref → REF_TABLE_OPEN STRING_LITERAL REF_TABLE_CLOSE REF_COL_OPEN STRING_LITERAL REF_COL_CLOSE
- Ref_Column → REF_COL_OPEN STRING_LITERAL REF_COL_CLOSE
- Constant → STRING_CONSTANT_OPEN STRING_LITERAL STRING_CONSTANT_CLOSE | INT_CONSTANT_OPEN INT_LITERAL INT_CONSTANT_CLOSE
- Group_By → GROUP_BY_OPEN ColumnList GROUP_BY_CLOSE
- Having → HAVING_OPEN Condition HAVING_CLOSE
- Order_By → ORDER_BY_OPEN Order_By_Inner ORDER_BY_CLOSE
- Order_By_Inner → ASC_OPEN Ref_Column ASC_CLOSE | DESC_OPEN Ref_Column DESC_CLOSE


Sample Parser output for test1.xml:
```
Successfully parsed. AST structure:
Query:
  Select:
    Column: class
    Column:
      Function: count
        Parameters:
          Column: *
    Column:
      Alias:
        Expression:
          Function: max
            Parameters:
              Column: stats
        As: max_stats
  From:
    Table: characters
    Table: games
  Where:
    Logical and:
      Left:
        Comparison (eq):
          Left:
            Reference: games.game
          Right: 'genshin'
      Right:
        Bracketed Expression:
          Logical or:
            Left:
              Comparison (eq):
                Left:
                  Reference: games.origin
                Right: 'USA'
            Right:
              Comparison (eq):
                Left:
                  Reference: games.origin
                Right: 'Japan'
  Group By:
    Column: class
  Having:
    Comparison (gt):
      Left:
        Function: count
          Parameters:
            Column: *
      Right: 3
  Order By:
    Column: class
    Direction: asc
```
- test7.xml - syntax error as doesn't have the referenced table for the referenced column
```
Error parsing file: Expected either:
1. Table and column reference (<ref_table>...<ref_col>)
2. String literal
3. Function call (count_func or max_func)
Got TokenType.REF_COL_OPEN instead
```
- test8.xml - syntax error - from clause should have `<table>..</table>` within them
```
Error parsing file: Table must be wrapped in <table> tags
```
- test9.xml - syntax error - doesn't have an argument for count_func
```
Error parsing file: Expected at least one function argument
```
- test10.xml - syntax error - has 2 string literals for rhs instead of 1 i.e. "num_of_cars""num_of_cars" instead of "num_of_cars"
```
Error parsing file: Unclosed alias RHS
```

## Execution 

- Git clone this repo 
- If you have python on your system, you can cd to project directory and first run the script : 
    ```
    python tokenizer.py
    ```
  Then run the script
    ```
    python parser.py
    ```
- You can alternatively run the Shell script. First make sure it is executable by changing permission :
   ```
   chmod +x run.sh
   ```
- Now Execute the Shell Script from the project directory :
    ```
    ./run.sh
    ```
- You can alternatively use docker if you have it installed. Run the below from the project directory to build the image.
    ``` 
    docker build -t parser . 
    ```
- Next run the image
    ``` 
    docker run parser 
    ```


## TEAM

- Navinashok Swaminathan (UNI : NS3886 )
- Shihao Wang (UNI : sw4016)














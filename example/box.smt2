(set-logic QF_LIA)

; Declare variables x and y as integers
(declare-const x Int)
(declare-const y Int)

; Assert the constraints
(assert (or (<= 2 y) (<= y 5)))
(assert (or (<= x 3) (<= y 5)))
(check-sat)


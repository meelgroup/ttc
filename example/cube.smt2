(set-logic QF_LIA)
(declare-fun x () Int)
(declare-fun y () Int)
(declare-fun z () Int)

(assert (<= (+ (* 2 x) (* 3 y) (* 2 z)) 10))
(assert (>= (+ (* 2 x) (* 3 y) (* 4 z)) -1))
(assert (<= (+ (* 4 x) (* -5 y) (* 2 z)) 10))
(assert (>= (+ (* 4 x) (* -5 y) (* 5 z)) 1))

(check-sat)

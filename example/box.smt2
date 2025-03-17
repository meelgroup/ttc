(set-logic QF_LIA)
(declare-fun x () Int)
(declare-fun y () Int)

(assert (<= (+ (* 2 x) (* 1 y)) 10))
(assert (>= (+ (* 2 x) (* 1 y)) (- 1)))
(assert (<= (+ (* 4 x) (* (- 5) y)) 10))
(assert (>= (+ (* 4 x) (* (- 5) y)) 1))

(check-sat)

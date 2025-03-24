
(set-logic QF_LRA)

(declare-const x Real)
(declare-const y Real)

(assert (or (and (> x 10) (< x 30) (> y 10) (< y 30))
            (and (> x 15) (< x 35) (> y 15) (< y 35))))

(check-sat)
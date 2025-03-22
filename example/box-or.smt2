(set-logic QF_LIA)

(declare-const x Int)
(declare-const y Int)

(assert (or (and (> x 40) (< x 45) (> y 20) (< y 25))
            (and (> x 10) (< x 15) (> y 30) (< y 35))))

(check-sat)
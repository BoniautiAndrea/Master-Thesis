;problem file of lunar lander domain
(define (problem problem_1)
    (:domain t_only)
    (:init 
        ;current initial position, modify only the first line of predicates unless having modified the size of the domain
        (current_t t_2) (current_vt vt_2)
        ;predicates needed to construct and connect the discrete domain
        ;limit cases included in next and prev predicates to allow limit cases in actions parameters
        (negative vt_-1) (negative vt_-2)
        (next t_-1 t_-2) (next t_0 t_-1) (next t_1 t_0) (next t_2 t_1) (next t_2 t_2)
        (next vt_-1 vt_-2) (next vt_0 vt_-1) (next vt_1 vt_0) (next vt_2 vt_1) (next vt_2 vt_2)
        (positive vt_1) (positive vt_2)
        (prev t_-2 t_-2) (prev t_-2 t_-1) (prev t_-1 t_0) (prev t_0 t_1) (prev t_1 t_2)
        (prev vt_-2 vt_-2) (prev vt_-2 vt_-1) (prev vt_-1 vt_0) (prev vt_0 vt_1) (prev vt_1 vt_2)
    )

    (:goal (and 
        (current_t t_0) (current_vt vt_0)
        )
    )
)
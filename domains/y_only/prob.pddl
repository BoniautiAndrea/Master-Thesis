;problem file of lunar lander domain
(define (problem problem_1)
    (:domain y_only)
    (:init 
        ;current initial position, modify only the first line of predicates unless having modified the size of the domain
        (current_y y_3) (current_vy vy_1)
        ;predicates needed to construct and connect the discrete domain
        ;limit cases included in next and prev predicates to allow limit cases in actions parameters
        (negative vy_-1) (negative vy_-2) (negative vy_-3)
        (next y_0 y_-1) (next y_1 y_0) (next y_2 y_1) (next y_3 y_2) (next y_3 y_3)
        (next vy_-2 vy_-3) (next vy_-1 vy_-2) (next vy_0 vy_-1) (next vy_1 vy_0) (next vy_1 vy_1)
        (positive vy_1)
        (prev y_-1 y_-1) (prev y_-1 y_0) (prev y_0 y_1) (prev y_1 y_2) (prev y_2 y_3)
        (prev vy_-3 vy_-3) (prev vy_-3 vy_-2) (prev vy_-2 vy_-1) (prev vy_-1 vy_0) (prev vy_0 vy_1)
    )

    (:goal (and 
        (current_y y_0) (current_vy vy_0)
        )
    )
)
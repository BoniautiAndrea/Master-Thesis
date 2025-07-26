;problem file of lunar lander domain
(define (problem problem_1)
    (:domain x_only)
    (:init 
        ;current initial position, modify only the first line of predicates unless having modified the size of the domain
        (current_x x_2) (current_vx vx_2)
        ;predicates needed to construct and connect the discrete domain
        ;limit cases included in next and prev predicates to allow limit cases in actions parameters
        (negative vx_-1) (negative vx_-2)
        (next x_-1 x_-2) (next x_0 x_-1) (next x_1 x_0) (next x_2 x_1) (next x_2 x_2)
        (next vx_-1 vx_-2) (next vx_0 vx_-1) (next vx_1 vx_0) (next vx_2 vx_1) (next vx_2 vx_2)
        (positive vx_1) (positive vx_2)
        (prev x_-2 x_-2) (prev x_-2 x_-1) (prev x_-1 x_0) (prev x_0 x_1) (prev x_1 x_2)
        (prev vx_-2 vx_-2) (prev vx_-2 vx_-1) (prev vx_-1 vx_0) (prev vx_0 vx_1) (prev vx_1 vx_2)
    )

    (:goal (and 
        (current_x x_0) (current_vx vx_0)
        )
    )
)
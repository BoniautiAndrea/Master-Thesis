;lunar lander discrete domain
;for solver reasons and limits it is not a numerical domain, the domain size is defined by constant values
;the non-determinism is induces by the discretization of the original domain, each constant is not just a
;singular value, but it represents an interval of the original continuous domain, except for 0 values
;ex. x_10 = (9,10]
; 2m 30s for expanded planning
(define (domain x_only)
    (:requirements :typing :conditional-effects :negative-preconditions :equality :non-deterministic)

    ;types used to reduce variable choices in predicates and to have a better understandable code
    (:types 
        value
        x_value vx_value - value
    )

    ;needed constants to define the discrete domain
    (:constants x_-2 x_-1 x_0 x_1 x_2 - x_value
                vx_-2 vx_-1 vx_0 vx_1 vx_2 - vx_value
    )

    (:predicates   
        ;current state definition x,y = cartesian position t(theta)=angle wrt x axis
        ;next and prev predicates used to connect domain values
        ;ex. from x_10 and x_9 -> (x_prev x_9 x_10) and (x_next x_10 x_9)
        (current_x ?x - x_value)    
        (current_vx ?vx - vx_value)
        ;predicates to define relations between constants
        (negative ?v - value)
        (next ?n ?v - value) 
        (positive ?v - value)  
        (prev ?p ?v - value)
    )

    ;Actions, to reduce computational time idle and main engine actions can just modify vertical motion
    ; and side engine actions can just modify horizontal and rotational motion

    ;idle action, no engine fired, the lander could just move in vertical direction, it actually can
    ;modify vertical velocity that then can induce the vertical motion
    (:action idle
        :parameters (?x_prev ?x ?x_next - x_value ?vx - vx_value)
        :precondition (and 
            (current_x ?x) (current_vx ?vx)
            (prev ?x_prev ?x)
            (next ?x_next ?x)
        )
        :effect (and
            (when
                (positive ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_next)) (and))
            )
            (when
                (negative ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_prev)) (and))
            )
        )
    )

    ;main engine motion, same logic as idle motion but inverse effect on vertical velocity
    (:action main_engine
        :parameters (?x_prev ?x ?x_next - x_value ?vx - vx_value)
        :precondition (and 
            (current_x ?x) (current_vx ?vx)
            (prev ?x_prev ?x)
            (next ?x_next ?x)
        )
        :effect (and
            (when
                (positive ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_next)) (and))
            )
            (when
                (negative ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_prev)) (and))
            )
        )
    )
    
    ;right engine action, can affect only horizontal and rotational velocity, then update x and t (theta)
    ;according to their sign respectively
    (:action right_engine
        :parameters (?x_prev ?x ?x_next - x_value ?vx_prev ?vx - vx_value)
        :precondition (and 
            (current_x ?x) (current_vx ?vx)
            (next ?x_next ?x)
            (prev ?x_prev ?x)
            (prev ?vx_prev ?vx)
        )
        :effect(and
            (oneof (and (not (current_vx ?vx)) (current_vx ?vx_prev)) (and))
            (when
                (positive ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_next)) (and))
            )     
            (when
                (negative ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_prev)) (and))
            )
        )
    )
    
    ;same logic as right engine action, but inverse effects
    (:action left_engine
        :parameters (?x_prev ?x ?x_next - x_value ?vx ?vx_next - vx_value)
        :precondition (and 
            (current_x ?x) (current_vx ?vx)
            (prev ?x_prev ?x)
            (next ?x_next ?x)
            (next ?vx_next ?vx)
        )
        :effect (and
            (oneof (and (not (current_vx ?vx)) (current_vx ?vx_next)) (and))
            (when
                (positive ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_next)) (and))
            )     
            (when
                (negative ?vx) (oneof (and (not (current_x ?x)) (current_x ?x_prev)) (and))
            )
        )
    )
)
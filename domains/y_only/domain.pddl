;lunar lander discrete domain
;for solver reasons and limits it is not a numerical domain, the domain size is defined by constant values
;the non-determinism is induces by the discretization of the original domain, each constant is not just a
;singular value, but it represents an interval of the original continuous domain, eycept for 0 values
;ey. y_10 = (9,10]
; 2m 30s for eypanded planning
(define (domain y_only)
    (:requirements :typing :conditional-effects :negative-preconditions :equality :non-deterministic)

    ;types used to reduce variable choices in predicates and to have a better understandable code
    (:types 
        value
        y_value vy_value - value
    )

    ;needed constants to define the discrete domain
    (:constants y_-1 y_0 y_1 y_2 y_3 - y_value
                vy_-3 vy_-2 vy_-1 vy_0 vy_1 - vy_value
    )

    (:predicates   
        ;current state definition y,y = cartesian position t(theta)=angle wrt y ayis
        ;next and prev predicates used to connect domain values
        ;ey. from y_10 and y_9 -> (y_prev y_9 y_10) and (y_next y_10 y_9)
        (current_y ?y - y_value)    
        (current_vy ?vy - vy_value)
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
        :parameters (?y_prev ?y ?y_next - y_value ?vy_prev ?vy - vy_value)
        :precondition (and 
            (current_y ?y) (current_vy ?vy)
            (prev ?y_prev ?y)
            (next ?y_next ?y)
            (prev ?vy_prev ?vy)
            ;(not (current_vy vy_-3))
            ;(not (current_vy vy_-2))
            ;(not (current_y y_0))
        )
        :effect (and
            (oneof (and (not (current_vy ?vy)) (current_vy ?vy_prev)) (and))
            (when
                (positive ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_next)) (and))
            )
            (when
                (negative ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_prev)) (and))
            )
        )
    )

    ;main engine motion, same logic as idle motion but inverse effect on vertical velocity
    (:action main_engine
        :parameters (?y_prev ?y ?y_next - y_value ?vy ?vy_next - vy_value)
        :precondition (and 
            (current_y ?y) (current_vy ?vy)
            (prev ?y_prev ?y)
            (next ?y_next ?y)
            (next ?vy_next ?vy)
        )
        :effect (and
            (oneof (and (not (current_vy ?vy)) (current_vy ?vy_next)) (and))
            (when
                (positive ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_next)) (and))
            )
            (when
                (negative ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_prev)) (and))
            )
        )
    )
    
    ;right engine action, can affect only horizontal and rotational velocity, then update y and t (theta)
    ;according to their sign respectively
    (:action right_engine
        :parameters (?y_prev ?y ?y_next - y_value ?vy - vy_value)
        :precondition (and 
            (current_y ?y) (current_vy ?vy)
            (next ?y_next ?y)
            (prev ?y_prev ?y)
            ;(not (current_y y_0))
            ;(not (current_y y_-1))
        )
        :effect(and
            (when
                (positive ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_next)) (and))
            )     
            (when
                (negative ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_prev)) (and))
            )
        )
    )
    
    ;same logic as right engine action, but inverse effects
    (:action left_engine
        :parameters (?y_prev ?y ?y_next - y_value ?vy - vy_value)
        :precondition (and 
            (current_y ?y) (current_vy ?vy)
            (prev ?y_prev ?y)
            (next ?y_next ?y)
            ;(not (current_y y_0))
            ;(not (current_y y_-1))
        )
        :effect (and
            (when
                (positive ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_next)) (and))
            )     
            (when
                (negative ?vy) (oneof (and (not (current_y ?y)) (current_y ?y_prev)) (and))
            )
        )
    )
)
;lunar lander discrete domain
;for solver reasons and limits it is not a numerical domain, the domain size is defined by constant values
;the non-determinism is induces by the discretization of the original domain, each constant is not just a
;singular value, but it represents an interval of the original continuous domain, except for 0 values
;ex. t_10 = (9,10]
; 2m 30s for expanded planning
(define (domain t_only)
    (:requirements :typing :conditional-effects :negative-preconditions :equality :non-deterministic)

    ;types used to reduce variable choices in predicates and to have a better understandable code
    (:types 
        value
        t_value vt_value - value
    )

    ;needed constants to define the discrete domain
    (:constants t_-2 t_-1 t_0 t_1 t_2 - t_value
                vt_-2 vt_-1 vt_0 vt_1 vt_2 - vt_value
    )

    (:predicates   
        ;current state definition x,y = cartesian position t(theta)=angle wrt x axis
        ;next and prev predicates used to connect domain values
        ;ex. from t_10 and t_9 -> (t_prev t_9 t_10) and (t_next t_10 t_9)
        (current_t ?t - t_value)    
        (current_vt ?vt - vt_value)
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
        :parameters (?t_prev ?t ?t_next - t_value ?vt - vt_value)
        :precondition (and 
            (current_t ?t) (current_vt ?vt)
            (prev ?t_prev ?t)
            (next ?t_next ?t)
        )
        :effect (and
            (when
                (positive ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_next)) (and))
            )
            (when
                (negative ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_prev)) (and))
            )
        )
    )

    ;main engine motion, same logic as idle motion but inverse effect on vertical velocity
    (:action main_engine
        :parameters (?t_prev ?t ?t_next - t_value ?vt - vt_value)
        :precondition (and 
            (current_t ?t) (current_vt ?vt)
            (prev ?t_prev ?t)
            (next ?t_next ?t)
        )
        :effect (and
            (when
                (positive ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_next)) (and))
            )
            (when
                (negative ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_prev)) (and))
            )
        )
    )
    
    ;right engine action, can affect only horizontal and rotational velocity, then update x and t (theta)
    ;according to their sign respectively
    (:action right_engine
        :parameters (?t_prev ?t ?t_next - t_value ?vt ?vt_next - vt_value)
        :precondition (and 
            (current_t ?t) (current_vt ?vt)
            (next ?t_next ?t)
            (prev ?t_prev ?t)
            (next ?vt_next ?vt)
        )
        :effect(and
            (oneof (and (not (current_vt ?vt)) (current_vt ?vt_next)) (and))
            (when
                (positive ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_next)) (and))
            )     
            (when
                (negative ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_prev)) (and))
            )
        )
    )
    
    ;same logic as right engine action, but inverse effects
    (:action left_engine
        :parameters (?t_prev ?t ?t_next - t_value ?vt_prev ?vt - vt_value)
        :precondition (and 
            (current_t ?t) (current_vt ?vt)
            (prev ?t_prev ?t)
            (next ?t_next ?t)
            (prev ?vt_prev ?vt)
        )
        :effect (and
            (oneof (and (not (current_vt ?vt)) (current_vt ?vt_prev)) (and))
            (when
                (positive ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_next)) (and))
            )     
            (when
                (negative ?vt) (oneof (and (not (current_t ?t)) (current_t ?t_prev)) (and))
            )
        )
    )
)
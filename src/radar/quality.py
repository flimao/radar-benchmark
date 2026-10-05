"""PoC quality policy: evaluation never implies automatic financial approval."""
from decimal import Decimal


def evaluate(checks, policy, *, comparable=True, comparability_reason='',
             reference=None, calculated=None, rounding_tolerance=0,
             previous=None, current=None, approved=False, alert_accepted=False):
    reasons = []
    comparability = 'COMPARAVEL' if comparable else 'NAO_COMPARAVEL'
    if not comparable and not comparability_reason:
        raise ValueError('Não comparabilidade exige justificativa.')
    if not comparable:
        reasons.append(comparability_reason)
    failures = [name for name in policy['required_checks'] if not checks.get(name, False)]
    failures += [name for name, passed in checks.items() if not passed and name not in failures]
    if failures:
        reasons.append('Controles essenciais reprovados: ' + ', '.join(failures))
        state = 'BLOQUEADO'
    else:
        state = 'APROVADO' if approved else 'REVISAO'
        if reference is not None and calculated is not None:
            reference, calculated = Decimal(str(reference)), Decimal(str(calculated))
            tolerance = max(Decimal(str(policy['reconciliation_absolute_usd_million'])),
                            abs(reference) * Decimal(str(policy['reconciliation_relative'])),
                            Decimal(str(rounding_tolerance)))
            if abs(calculated - reference) > tolerance:
                state = 'REVISAO'
                reasons.append('Reconciliação fora da tolerância.')
        if previous is not None and current is not None:
            previous, current = Decimal(str(previous)), Decimal(str(current))
            variation = (abs(current - previous) / abs(previous)) if previous else None
            if (variation is None and current != 0) or (variation is not None and variation > Decimal(str(policy['variation_alert_relative']))):
                reasons.append('Variação exige revisão: base anterior zero.' if previous == 0 else 'Variação superior a 30%.')
                if state != 'REVISAO':
                    state = 'ALERTA'
    # Review unresolved reconciliation is never bypassed by accepting an alert.
    publishable = state == 'APROVADO' or (state == 'ALERTA' and approved and alert_accepted)
    return {'state': state, 'comparability': comparability, 'reasons': reasons,
            'publishable': publishable, 'eligible_for_comparison': publishable and comparable}

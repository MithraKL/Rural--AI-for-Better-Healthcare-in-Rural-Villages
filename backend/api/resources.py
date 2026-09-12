from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Village, InterventionOption, PriorityScore, ResourcePool, ResourceAllocation
from backend.schemas import ResourcePoolIn, ResourceOptimizationResult, ResourceAllocationOut
from backend.optimization.resource_optimizer import ResourcePoolState, OptimizerCandidate, optimize

router = APIRouter()


@router.post("/optimize", response_model=ResourceOptimizationResult)
def optimize_resources(pool_in: ResourcePoolIn, db: Session = Depends(get_db)):
    priorities = {p.village_id: p for p in db.query(PriorityScore).all()}

    # Best (highest impact-per-resource) intervention option per village
    best_by_village: dict[int, InterventionOption] = {}
    for opt in db.query(InterventionOption).order_by(InterventionOption.impact_per_resource.desc()).all():
        if opt.village_id not in best_by_village:
            best_by_village[opt.village_id] = opt

    villages = {v.id: v for v in db.query(Village).all()}

    candidates = []
    for village_id, opt in best_by_village.items():
        priority = priorities.get(village_id)
        village = villages.get(village_id)
        if not priority or not village:
            continue
        candidates.append(OptimizerCandidate(
            village_id=village_id, village_name=village.name, priority_score=priority.priority_score,
            population=village.population, intervention_name=opt.intervention_name, category=opt.category,
            problem_tag=opt.problem_tag, cost_estimate_inr=opt.cost_estimate_inr,
            expected_impact_score=opt.expected_impact_score, impact_per_resource=opt.impact_per_resource,
            coverage_population=opt.coverage_population,
        ))

    pool_state = ResourcePoolState(**pool_in.model_dump(exclude={"name"}))
    allocations, remaining = optimize(pool_state, candidates)

    pool_row = ResourcePool(name=pool_in.name, **pool_in.model_dump(exclude={"name"}))
    db.add(pool_row)
    db.flush()
    for a in allocations:
        db.add(ResourceAllocation(
            pool_id=pool_row.id, village_id=a.village_id,
            allocated_budget_inr=a.allocated_budget_inr, allocated_mmus=a.allocated_mmus,
            allocated_vaccine_doses=a.allocated_vaccine_doses, allocated_medicine_units=a.allocated_medicine_units,
            allocated_workers=a.allocated_workers, expected_impact_score=a.expected_impact_score,
            population_covered=a.population_covered, rank=a.rank,
        ))
    db.commit()

    return ResourceOptimizationResult(
        pool=pool_in,
        allocations=[
            ResourceAllocationOut(
                village_id=a.village_id, village_name=a.village_name, intervention_name=a.intervention_name,
                allocated_budget_inr=a.allocated_budget_inr, allocated_mmus=a.allocated_mmus,
                allocated_vaccine_doses=a.allocated_vaccine_doses, allocated_medicine_units=a.allocated_medicine_units,
                allocated_workers=a.allocated_workers, expected_impact_score=a.expected_impact_score,
                population_covered=a.population_covered, rank=a.rank,
            )
            for a in allocations
        ],
        remaining_budget_inr=remaining.budget_inr, remaining_mmus=remaining.mobile_medical_units,
        remaining_vaccine_doses=remaining.vaccine_doses, remaining_medicine_units=remaining.medicine_units,
        total_expected_impact=round(sum(a.expected_impact_score for a in allocations), 1),
        total_population_covered=sum(a.population_covered for a in allocations),
    )

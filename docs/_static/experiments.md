@startuml

skinparam linetype ortho
skinparam package {
    BackgroundColor #CCCCCC
}
skinparam class {
    BackgroundColor PaleGreen
}

package experiments {
    class ExperimentRunner {
        + run(experiment: Experiment)
    }

    class Experiment <<abstract>> {
        - stages: List[Stages]
        + executeStages(...)
    }

    class Stage <<Command>> {
        + execute(...)
    }

    ExperimentRunner --> Experiment: <<uses>>
    Experiment *-r- Stage
}

@enduml
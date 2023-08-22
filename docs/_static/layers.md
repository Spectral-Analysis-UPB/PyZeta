@startuml

skinparam linetype ortho
skinparam component {
    BackgroundColor DarkGrey
}
skinparam note {
    BackgroundColor #CCCCCC
}

[view] as view
[experiments] as exps
[configuration management] as config
[               persistence               ] as pers

view ---> pers
note right on link
    display metadata
end note
exps ---> config
note left on link
    convert to context
end note
config ---> pers
note right on link
    supply metadata
end note

note right of pers
    - homogeneous data
      format
    - converts and stores
      metadata
end note

note left of view
    cli
    browser
    gui
    ...
end note

@enduml
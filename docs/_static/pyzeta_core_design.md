@startuml

left to right direction
skinparam linetype ortho

skinparam package {
    BackgroundColor #CCCCCC
}

skinparam class {
    BackgroundColor PaleGreen
}

skinparam titleBorderRoundCorner 15
skinparam titleBorderThickness 2
skinparam titleBorderColor black
skinparam titleBackgroundColor SeaGreen

title "PyZeta Core Components and Auxiliary Packages"

package core #FFD700 {
    package symmetries #AAAAAA {
        interface SymmetryGroup <<interface>> { }
    }

    package zetas #AAAAAA {
        abstract class Zeta <<abstract>> {
            {abstract} #calcA(...)
            {abstract} -calcD(...)
            {abstract} +calcZeta(...)
            +__call__(...)
        }

        Zeta <|-- RuelleZeta
        RuelleZeta <|-right- WeightedZeta
        Zeta <|-- SelbergZeta

        Zeta o-- "1" SymmetryGroup
    }

    package dynamics #AAAAAA {
        package symbolic_dynamics {
            class SymbolicDynamics { }

            Zeta o-- SymbolicDynamics
            SymbolicDynamics <|-- ReducedSymbolicDynamics
            ReducedSymbolicDynamics o-- "1" SymmetryGroup
        }

        package function_dynamics {
            abstract class FunctionSystem <<abstract>> { }

            FunctionSystem "1" --o Zeta
            FunctionSystem <|-- MoebiusSystem
            FunctionSystem <|-- GaussSystem
            MoebiusSystem <|-- FunnelSystem
            MoebiusSystem <|-- SchottkySystem

            FunctionSystem o-- "1" SymmetryGroup
        }
    }

    package distributions #AAAAAA {
        class RuelleDistribution { }

        RuelleDistribution o-- WeightedZeta
        RuelleDistribution o-- SymmetryGroup
    }
}

package utilities {
    interface ResonanceFinder <<interface>> {
        +complex[] resonances
        +int[] orders
        +__init__(systemType: FunctionSystemType, **systemKwargs: object)
        +void calculateResonances(...)
    }

    ResonanceFinder o-- Zeta

    class HausdorffDimension <<static>> {
        {static} -calculateFromPressure(...)
        {static} -calculateFromResonances(...)
        {static} +calculateDimension(..., from: Enum)
    }

    HausdorffDimension o-- FunctionSystem: {transient}
    HausdorffDimension o-right- TopologicalPressure: {transient}
    HausdorffDimension o-left- ResonanceFinder: {transient}
}

package experiments #AAAAAA {
    package configuration {
        class Configuration { }

        class ConfigurationManager { }
    }

    abstract class ExperimentTemplate <<abstract>> { }

    class ExperimentRunner { }

    ExperimentRunner -left-> ExperimentTemplate
    ConfigurationManager -left-> Configuration
}

package persistence {
    class ResonanceHandler { }

    class DistributionHandler { }
}

package view #AAAAAA {
    package gui {
        class ResonanceSelector { }

        class RuelleDistributionViewer { }
    }

    package cli {
        class PyZetaEntry <<static>> { }
    }
}

persistence -[hidden]-> experiments
experiments -[hidden]-> framework
view -[hidden]-> core

package geometry {
    class SL2R { }

    class SU11 { }

    class Geodesic { }

    Geodesic -[hidden]-> SL2R
    Geodesic -[hidden]-> SU11
    SL2R -[hidden]-> SU11
}

package framework #AAAAAA {
    package feature_toggle {
        class FeatureFlag { }

        class ToggleCollection { }
    }

    package pyzeta_logging {
        class LogManager { }
    }

    package settings {
        interface CoreSettingsService <<interface>> { }
    }

    package analyzers {
        class PerformanceAnalyzer { }
    }

    package plugins {
        class PyZetaPlugin { }

        class PluginLoader { }

        class PluginManager { }

        PluginManager -left-> PluginLoader
        PluginManager -right-o PyZetaPlugin
    }

    package ioc {
        class ContainerProvider <<static>> {
            {static} getContainer(...)
        }

        class IoCContainer {
            void registerAsSingleton(...)
            void registerAsTransient(...)
            Object tryResolve(...)
            void seal()
            bool isSealed()
        }
    }

    package initialization {
        class InitializationHandler <<static>> { }
    }

    ioc -[hidden]-> settings
    ioc -[hidden]-> plugins
    ioc -[hidden]-> analyzers
    pyzeta_logging -[hidden]-> initialization
}

view --> geometry
view --> persistence

view -[hidden]-> framework
geometry -[hidden]-> framework
persistence -[hidden]-> framework
core -[hidden]-> framework
utilities -[hidden]-> framework

@enduml
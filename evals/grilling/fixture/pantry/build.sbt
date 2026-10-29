ThisBuild / scalaVersion := "3.3.4"
ThisBuild / organization := "dev.pantry"

lazy val core = project
  .settings(name := "pantry-core")

lazy val api = project
  .dependsOn(core)
  .settings(name := "pantry-api")

lazy val worker = project
  .dependsOn(core)
  .settings(name := "pantry-worker")

# Sistema de Gestión de Prácticas Preprofesionales (SGPP)
## Documento de Especificación Macro y Vista General del Proyecto

---

## 1. Introducción y Propósito del Sistema

El **Sistema de Gestión de Prácticas Preprofesionales (SGPP)** es una solución de software de escritorio de alta cohesión diseñada específicamente para automatizar, centralizar y auditar integralmente el ciclo de vida de las prácticas laborales de estudiantes universitarios. 

El propósito fundamental de la plataforma es servir como un puente operativo y unificador de datos entre tres pilares esenciales: el **Estudiante** postulante, las **Empresas** del sector productivo u organismos públicos y la **Institución Universitaria** (representada por la Coordinación de Vinculación y los Tutores Académicos). 

A diferencia de los flujos analógicos o distribuidos tradicionales basados en correos y formatos físicos dispersos, el SGPP unifica todas las transacciones, validaciones reglamentarias y el control documental en un entorno guiado por reglas de negocio estrictas, garantizando la trazabilidad desde la postulación inicial hasta el cierre de actas institucionales.

---

## 2. Descripción del Problema y Justificación

En el ecosistema académico actual, la gestión de prácticas preprofesionales enfrenta desafíos operativos críticos debido a la asincronía de los actores involucrados. Los principales dolores identificados incluyen:

* **Dispersión y Opacidad de Ofertas:** Los estudiantes carecen de un canal centralizado donde analizar vacantes que se alineen con sus intereses profesionales específicos.
* **Sobrecarga Administrativa en la Coordinación:** La validación manual de requisitos indispensables (malla académica, verificación de créditos, ciclos cursados y vigencia de convenios empresariales) consume tiempo operativo crítico y es susceptible a errores humanos.
* **Falta de Seguimiento en Tiempo Real:** El control de las bitácoras semanales de actividades y las evaluaciones concurrentes de los tutores (académicos y empresariales) tiende a fragmentarse, retrasando los cierres oficiales del proceso.

La justificación de este proyecto radica en la implantación de una arquitectura limpia orientada al dominio, que automatice las barreras burocráticas, aplique algoritmos de priorización equitativos para los estudiantes y blinde legalmente a la universidad mediante la verificación automatizada del estado de convenios y cartas compromiso.

---

## 3. Arquitectura Tecnológica y Filosofía de Diseño

El sistema está concebido bajo rigurosos estándares de ingeniería de software modernos, adaptados a un flujo de desarrollo autónomo:

* **Patrón de Arquitectura Base:** Arquitectura en capas guiada por el patrón **Model-View-Controller (MVC)**, extendido con una capa independiente de **Servicios** para el aislamiento de las reglas de negocio y una capa de **Persistencia** abstracta.
* **Evolución del Almacenamiento (Data Agnostic):** El diseño inicial implementa persistencia de datos plana mediante estructuras vectoriales en archivos locales (formatos **.dat**). No obstante, la capa de datos se encuentra completamente desacoplada mediante abstracciones puras, preparada estructuralmente para realizar una migración transparente hacia cualquier motor de base de datos.
* **Paradigmas Combinados:** Se explota la **Programación Orientada a Objetos (POO)** para el modelado semántico de las entidades del dominio, interactuando en sinergia con la **Programación Funcional** para los procesos puros de filtrado de datos, ordenamiento de ternas y cálculos estadísticos de reportes.
* **Ecosistema Gráfico:** La interfaz de usuario se construye de forma modular y escalable mediante **PyQt6 / PySide6** utilizando ventanas principales (`MainWindow`) independientes por cada rol de usuario, garantizando el desacoplamiento visual y la separación absoluta de responsabilidades gráficas.

---

## 4. Actores del Sistema y Roles Operativos

El SGPP interactúa dinámicamente con seis (6) actores del negocio, cada uno provisto de un entorno operativo exclusivo y aislado:

1. **Administrador del Sistema:** Actor con privilegios de sistema. Gestiona usuarios, roles y reportes.
2. **Estudiante:** Actor transaccional. Registra su perfil, postula a vacantes priorizadas, genera solicitudes excepcionales de validación para empresas autogestionadas y reporta de forma semanal su bitácora de actividades junto con la carga de los formularios de evaluación correspondientes.
3. **Empresa:** Actor oferente. Publica y mantiene plazas de prácticas disponibles, evalúa los expedientes académicos curriculares y las hojas de vida enviadas dentro de las ternas universitarias, y selecciona formalmente al candidato idóneo.
4. **Coordinador de Vinculación:** Máxima autoridad regulatoria y cerebro del sistema. Supervisa el cumplimiento de los ciclos académicos, valida los convenios institucionales vigentes, emite de forma digital certificados u oficios institucionales, conforma las ternas y autoriza el cierre definitivo de las prácticas tras aprobar el Formulario 1 matriz.
5. **Tutor Académico:** Miembro del cuerpo docente designado para el seguimiento pedagógico y técnico del estudiante. Valida o rechaza el plan diario/semanal de actividades en el sistema y emite la rúbrica cuantitativa final (Formulario 2).
6. **Tutor Empresarial:** Supervisor asignado por la organización receptora dentro del espacio laboral. Certifica la asistencia del estudiante, co-valida las actividades ejecutadas y provee la evaluación de desempeño corporativo (Formulario 3).

---

## 5. Reglas de Negocio Críticas y Flujo Operativo Matriz

El software rige su comportamiento interno de acuerdo con las siguientes directrices inviolables del caso de estudio:

* **Control de Concurrencia de Prácticas:** Un estudiante bajo ninguna circunstancia puede poseer más de una (1) práctica con estado "Activa" de forma simultánea en los registros del sistema.
* **Algoritmo de Priorización de Postulaciones:** Al desplegar el banco de ofertas de prácticas, el motor de negocio prioriza automáticamente a aquellos estudiantes matriculados en el **sexto ciclo académico o superior** que **no registren** antecedentes de prácticas aprobadas previamente.
* **Mecanismo de Selección por Ternas:** El proceso de asignación estándar requiere que el Coordinador agrupe un conjunto de postulaciones elegibles en una estructura denominada **Terna** para ser despachada a la Empresa. En el momento en que la Empresa ejecuta la aceptación de un estudiante de la terna, el sistema altera automáticamente el estado de los demás integrantes a "Rechazados para esta Oferta" y da de alta la entidad **Práctica Profesional** para el alumno seleccionado.
* **Vía Excepcional (Empresa Propia):** Si un estudiante gestiona una plaza laboral por iniciativa propia y cuenta con el respaldo corporativo, el flujo tradicional de ternas se omite. El estudiante genera una *Solicitud de Autorización*, la cual, al ser aprobada digitalmente por el Coordinador tras verificar los requisitos mínimos, crea de manera directa la *Práctica Profesional*.
* **Garantía Legal (Carta Compromiso):** El sistema exige la validez de un *Convenio de Vinculación* activo con la empresa. En caso de no existir un convenio vigente en los registros, se dispara obligatoriamente la emisión, control de copias físicas y firma de una *Carta Compromiso* de manera previa al inicio operativo de las actividades.
* **Ciclo de Vida Documental de Formularios:**
  * El **Formulario 1 (Documento Matriz de Inicio)** se registra obligatoriamente al arrancar las prácticas con estado "Presentado".
  * El **Formulario 2 (Evaluación del Tutor Académico)** y el **Formulario 3 (Evaluación del Tutor Empresarial)** se cumplimentan exclusivamente en la fase de cierre.
  * La práctica muta a su estado final de "Aprobada Oficialmente" únicamente cuando el Coordinador valida satisfactoriamente la consistencia de los formularios 2 y 3, permitiéndole cambiar el estado del Formulario 1 a "Aprobado".
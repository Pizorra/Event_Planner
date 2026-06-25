# Planificador de Eventos con dominio predeterminado de DnD

## Que hace el programa
La funcionalidad es similar a la de un Calendario,se elige una fecha y un lapso de tiempo en esta y se decide planificar un evento con los recursos y detalles que desee el usuario,en dependencia de los recursos utilizados,si estan disponibles,si no existen restricciones entre ellos entonces se añade el evento a un calendario que da todos los detalles de este y permite cancelarlo,el programa lleva el inventario de que esta disponible en cada momento y a su vez las restricciones existentes para cada dominio.

## Como lo diseñaste y por que tomaste las decisiones que tomaste

Decidi que queria hacer una aplicacion que actuase como una plantilla adaptable a cualquier dominio que se le pueda añadir,si tenemos en cuenta que se pueden añadir las restricciones o quitar las que se deseen y cambiar los recursos por los que sean necesarios y modelar las restricciones entre estos entonces la app funciona para cualquier dominio en el que se desee,haciendo las configuraciones antes por supuesto,pero sin necesidad de borrar codigo ni cambiar la logica del proyecto.Tome DnD como dominio predeterminado por el simple hecho de ser un hobbie para mi y por tanto inspirarme facilmente.Streamlit por ser una interfaz intuitiva y facil de aprender.

## Que aprendiste durante el desarrollo

Aprendi manejo de errores,programacion de interfaces y objetos,persistencia de datos,paciencia y tunel carpiano.

## Como se usa el programa

En el repositorio ejecutar **streamlit run app.py** 
Una vez dentro puedes programar eventos teniendo en cuenta las restricciones dadas,poner un nommbre de evento y asignar los recursos,si el evento no se puede llevar a cabo la app no añade el evento y da las razones por las cuales no se lleva a cabo,en dependencia del error puede ofrecer una solucion,por ejemplo si hay dos eventos que en el mismo intervalo de tiempo usan los mismos recursos esta da el siguiente intervalo de tiempo donde estan libre estos recursos para poder programar el evento.

## Dificultades que encontraste y como las resolviste

Las mayores dificultades fueron lograr que los errores fueran mostrados de forma correcta,por la forma en la que funciona streamlit los errores que se trataban salian y paraban la aplicacion al completo,y ahi debia ser reiniciada desde la misma interfaz,no recuerdo como lo resolvi pues termine el proyecto hace mas de 4 meses,otra de las dificultades fue la programacion de ciertas restricciones que actualmente funcionan de forma muy fuerte,esto queriendo decir que son las que mas detienen la app cuando se programa un evento que no puede ser.




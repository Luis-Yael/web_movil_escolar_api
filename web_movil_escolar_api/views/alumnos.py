from django.db.models import *
from django.db import transaction
from web_movil_escolar_api.serializers import UserSerializer
from web_movil_escolar_api.serializers import *
from web_movil_escolar_api.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group

class AlumnosAll(generics.CreateAPIView):
    #Verificar si el usuario esta autenticado
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active = 1).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        
        return Response(lista, 200)
    
class AlumnosView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación
    
    #Obtener alumno por ID
    # TODO: Agregar obtención de alumno por ID
    
    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data)
        if user.is_valid():
            #Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message":"Username "+email+", is already taken"},400)

            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = 1)


            user.save()
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            #Create a profile for the user
            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data["matricula"],
                                            curp= request.data["curp"].upper(),
                                            rfc= request.data["rfc"].upper(),
                                            fecha_nacimiento= request.data["fecha_nacimiento"],
                                            edad= request.data["edad"],
                                            telefono= request.data["telefono"],
                                            ocupacion= request.data["ocupacion"])
            alumno.save()

            return Response({"Alumno creado con ID: ": alumno.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar datos del alumno
    # TODO: Agregar actualización de alumnos
    
    # Eliminar alumno con delete (Borrar realmente)
    # TODO: Agregar eliminación de alumnos
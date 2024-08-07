from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import *
from app.forms import  ParametrosGeneralesPrediccionForm, PromedioMovilPonderadoForm

bp = Blueprint('demanda_predecida', __name__, url_prefix='/demanda_predecida')

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    promedio_movil_ponderado_form=PromedioMovilPonderadoForm()
    promedio_movil_ponderado_form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    
    errores = ErrorDemandaPredecida.query.all()
    return render_template('demanda_predecida/index.html', form=form , errores=errores,promedio_movil_ponderado_form=promedio_movil_ponderado_form)

@bp.route('/parametros', methods=['GET', 'POST'])
def parametros():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    
    return render_template('demanda_predecida/index.html', form=form )


@bp.route('/promedio_movil', methods=['GET', 'POST'])
def promedio_movil():
    form = ParametrosGeneralesPrediccionForm()

    if form.validate_on_submit():
        articulo_id = form.articulo_id.data
        periodos = form.cantidad_periodos.data
        
        try:
            errorD=DemandaPredecida.error_predecir_promedio_movil(articulo_id,periodos)
            prediccion = DemandaPredecida.predecir_promedio_movil(articulo_id, periodos)
            flash(f'Demanda predecida usando Promedio Móvil: {prediccion}', 'success')
            nueva_demanda_predecida = DemandaPredecida(
                    cantidad_periodos=periodos,
                    articulo_id=articulo_id,
                    nombreMetodo= 'promedio movil',
                    error_DP=errorD
                ) 
            try:
                db.session.add(nueva_demanda_predecida)
                db.session.commit()
                flash('Demanda error predecida guardada con éxito!', 'success')
            except ValueError as e:
                flash(f'no se pudo crear la clase error 1: {str(e)}', 'danger') 
            return redirect(url_for('demandaPredecida.index'))          
        except ValueError as e:
            flash(f'no se pudo crear la clase error 2: {str(e)}', 'danger')
        return redirect(url_for('demanda_predecida.idex'))
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/promedio_movil_ponderado', methods=['GET', 'POST'])
def promedio_movil_ponderado():
    flash('promedio movil ponderado', 'danger')   
    form = PromedioMovilPonderadoForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        articulo_id = form.articulo_id.data
        periodos = form.cantidad_periodos.data
        factores_ponderacion = [float(f.factor.data) for f in form.factores_ponderacion]
        
        try:
            
            error = DemandaPredecida.error_predecir_promedio_movil_ponderado(articulo_id, periodos, factores_ponderacion)
            flash(f'Error calculado con exito:', 'success')
            erroDemandaPredecida = ErrorDemandaPredecida(
                    articulo_ID=articulo_id,
                    error_DP=error,
                    nombreMetodo= 'promedio movil ponderado',
                    #metodo_calculo_error=ParametrosGeneralesPrediccion.query.first().modelo_calculo_error.nombre,
                    factores_de_ponderacion= str(factores_ponderacion)
                ) 
            try:
                db.session.add(erroDemandaPredecida)
                db.session.commit()
                flash('Error generado con éxito', 'success')
                return render_template('demanda_predecida/index.html', form=form)
            except Exception as e:
                db.session.rollback()
                flash(f'Error al generar el error con PMP: {str(e)}', 'danger')      
        
        except ValueError as e:
            flash(str(e), 'danger')

        return render_template('demanda_predecida/index.html', form=form)
    
    if form.errors:
        flash(f'Errores en el formulario: {form.errors}', 'danger')
        print("Errores del formulario:", form.errors) 
        
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/promedio_movil_suavizado', methods=['GET', 'POST'])
def promedio_movil_suavizado():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]
    
    if form.validate_on_submit():
        articulo_id = form.articulo_id.data
        alfa = form.alfa.data
        prediccion_raiz = form.prediccion_raiz.data
        periodos=form.cantidad_periodos.data

        try:
            errorD=DemandaPredecida.error_predecir_promedio_movil_suavizado(articulo_id,alfa,prediccion_raiz )
            prediccion = DemandaPredecida.predecir_promedio_movil_suavizado(articulo_id, alfa, prediccion_raiz)
            flash(f'Demanda predecida usando Promedio Móvil Suavizado: {prediccion}', 'success')
            nueva_demanda_predecida = DemandaPredecida(
                    cantidad_periodos=periodos,
                    alfa=alfa,
                    articulo_id=articulo_id,
                    nombreMetodo= 'promedio movil suavizado',
                    error_DP=errorD
                ) 
            try:
                db.session.add(nueva_demanda_predecida)
                db.session.commit()
                flash('Demanda error predecida guardada con éxito!', 'success')
            except ValueError as e:
                flash(str(e), 'danger')
            return redirect(url_for('demandaPredecida.get_error'))          

        except ValueError as e:
            flash(str(e), 'danger')
        return redirect(url_for('demanda_predecida.resultados'))
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/regresionLineal', methods=['GET', 'POST'])
def regresion_lineal():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        try:
            articulo_id = form.articulo_id.data
            prediccion = DemandaPredecida.predecir_regresion_lineal(articulo_id)
            flash(f'Predicción: {prediccion}', 'success')
            errorD=DemandaPredecida.error_predecir_regresion_lineal(articulo_id )

            nueva_demanda_predecida = DemandaPredecida(
                    
                    articulo_id=articulo_id,
                    nombreMetodo= 'regresion lineal',
                    error_DP=errorD

                ) 
            try:
                db.session.add(nueva_demanda_predecida)
                db.session.commit()
                flash('Demanda error predecida guardada con éxito!', 'success')
            except ValueError as e:
                flash(str(e), 'danger')
            return redirect(url_for('demandaPredecida.get_error'))          
    
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('demanda_predecida/index.html', form=form)

@bp.route('/ajusteEstacional', methods=['GET', 'POST'])
def ajuste_estacional():
    form = ParametrosGeneralesPrediccionForm()
    form.articulo_id.choices = [(m.id, m.nombre_articulo) for m in Articulo.query.all()]

    if form.validate_on_submit():
        try:
            
            articulo_id = form.articulo_id.data
            indices_estacionales = [1.0] * 12  # Aquí puedes definir los índices estacionales adecuados
            predicciones = DemandaPredecida.predecir_ajuste_estacional(articulo_id, indices_estacionales)
            flash(f'Predicciones: {predicciones}', 'success')
            
            nueva_demanda_predecida = DemandaPredecida(
                    
                    articulo_id=articulo_id,
                    nombreMetodo= 'ajuste estacional'
                ) 
            try:
                db.session.add(nueva_demanda_predecida)
                db.session.commit()
                flash('Demanda error predecida guardada con éxito!', 'success')
            except ValueError as e:
                flash(str(e), 'danger')
            return redirect(url_for('demandaPredecida.get_error'))          

        except Exception as e:
            flash(str(e), 'danger')
    return render_template('demanda_predecida/index.html', form=form)


@bp.route('/resultados', methods=['GET'])
def resultados():
    demandas_predecidas = DemandaPredecida.query.all()
    return render_template('demanda_predecida/index.html', demandas_predecidas=demandas_predecidas)

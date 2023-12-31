from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.models import Tiket, TiketAttachment, db, hashids
from app.whatsapp_verification_api import OTPSession
from app.messaging import KamulyoTiketCreatedMessage


bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    return redirect(url_for('main.buat_tiket_form'))


@bp.route('/buat-tiket', methods=['GET', 'POST'])
def buat_tiket_form():
    if request.method == 'POST':
        jenis = request.form.get('jenis', '').strip()
        nama = request.form.get('nama', '').strip()
        nohp = request.form.get('nomorHp', '').strip()
        nik = request.form.get('nik', '').strip()
        subjek = request.form.get('subjek', '').strip()
        narasi = request.form.get('narasi', '').strip()
        is_publik = request.form.get('isPublik') == '1'
        auth_token = request.form.get('authToken')
        lampirans = request.files.getlist('lampiran')

        if not (jenis and nama and nohp and subjek and narasi and auth_token):
            abort(400)

        tiket = Tiket(jenis, nama, nohp, subjek, narasi, is_publik)
        if nik:
            tiket.nik = nik

        otp_session = OTPSession(nohp)

        if not tiket.validate():
            flash('Data tidak valid!', 'danger')
        elif not otp_session.verify_auth_token(auth_token):
            flash('Token verifikasi tidak valid. Silakan coba lagi dan pastikan nomor HP sudah terverifikasi.',
                  'danger')
        else:
            otp_session.revoke_auth_token()
            db.session.add(tiket)
            db.session.commit()

            for lampiran in lampirans:
                if not lampiran.filename:
                    continue

                unique_filename = f'{tiket.public_id}_{lampiran.filename}'
                new_lampiran = TiketAttachment.new_from_stream(tiket_id=tiket.id,
                                                               stream=lampiran.stream,
                                                               filename=unique_filename)
                db.session.add(new_lampiran)

            KamulyoTiketCreatedMessage(tiket).send()

            db.session.commit()

            return render_template('form_next.html', tiket=tiket)

    return render_template('index.html')


@bp.route('/tiket')
def cari_tiket():
    tiket_public_id = request.args.get('idTiket')
    next_url = request.args.get('next', '/')

    if not tiket_public_id:
        flash('ID tiket tidak boleh kosong!', 'danger')
        return redirect(next_url)

    tiket = Tiket.from_public_id(tiket_public_id)
    if not tiket:
        flash('Tiket tidak ditemukan!', 'danger')
        return redirect(next_url)

    return redirect(url_for('main.status_tiket', tiket_id=tiket.public_id))


@bp.route('/tiket/<tiket_id>')
@hashids.decode_or_404('tiket_id', first=True)
def status_tiket(tiket_id):
    tiket = Tiket.query.filter_by(id=tiket_id).first_or_404()
    tiket.dilihat_count += 1
    db.session.commit()
    return render_template('status_tiket.html', tiket=tiket)


@bp.route('/papan-aduan-publik')
def papan_aduan_publik():
    tikets = Tiket.query.filter_by(is_publik=True).all()
    return render_template('papan_aduan_publik.html', tikets=tikets)


@bp.route('/soal-sering-ditanya')
def soal_sering_ditanya():
    return render_template('soal_sering_ditanya.html')

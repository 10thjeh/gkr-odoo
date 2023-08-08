from odoo import models, fields, api
import json

class Anggota(models.Model):
    _name = 'gkr.anggota'
    _description = 'anggota'

    """Data Diri"""

    name = fields.Char(string='Nama')
    
    foto = fields.Binary(
        string='Foto',
    )
    
    no_telpon = fields.Char(
        string='Nomor Telepon',
    )
    email = fields.Char(
        string='E-Mail'
    )
    tempat_lahir_id = fields.Char(
        string='Tempat Lahir',
    )
    
    tanggal_lahir = fields.Date(
        string='Tanggal Lahir'
    )
    jenis_kelamin = fields.Selection([
        ('L', 'Laki-Laki'),
        ('P', 'Perempuan')
    ], string='Jenis Kelamin',
       default='L'
       )

    pendidikan = fields.Selection([
        ('tidak_sekolah', 'Tidak Sekolah'),
        ('sd','Sekolah Dasar'),
        ('smp','Sekolah Menengah Pertama'),
        ('smak','Sekolah Menengan Atas / Kejuruan'),
        ('d1', 'Diploma 1'),
        ('d2','Diploma 2'),
        ('d3','Diploma 3'),
        ('s1','Diploma 4/Sarjana 1'),
        ('s2','Sarjana 2'),
        ('s3','Sarjana 3'),
        ('lainnya','Lainnya'),
    ])

    pendidikan_notes = fields.Char(
        string='Keterangan'
    )
    
    """Data Gereja"""

    nomor_anggota = fields.Char(string='Nomor Anggota')
    tanggal_gabung = fields.Date(string='Tanggal Gabung')
    dibaptis = fields.Boolean(string='Sudah dibaptis?')
    meninggal = fields.Boolean(string='Meninggal?')
    aktif = fields.Boolean(string='Anggota Aktif')
    jabatan = fields.Selection(
        string='Jabatan',
        selection=[
            ('anggota', 'Anggota / Jemaat'), 
            ('karyawan', 'Karyawan'),
            ('hamba_tuhan_pdt', 'Hamba Tuhan / Pendeta'),
            ],
        default='anggota'
        
    )
    

    hubungan_anggota_ids = fields.One2many(
        string='',
        comodel_name='gkr.anggota.lines',
        inverse_name='anggota_id',
    )

    atestasi_masuk = fields.Boolean(string='Atestasi Masuk')
    tanggal_atestasi_masuk = fields.Date(
        string='Tanggal Masuk',
        default=fields.Date.context_today,
    )
    gereja_asal_id = fields.Many2one(comodel_name='gkr.gereja', string='Gereja Asal')
    
    atestasi_keluar = fields.Boolean(string='Atestasi Keluar')
    tanggal_atestasi_keluar = fields.Date(
        string='Tanggal Keluar',
        default=fields.Date.context_today,
    )
    gereja_tujuan_id = fields.Many2one(comodel_name='gkr.gereja', string='Gereja Tujuan')

    """Data Baptis"""

    nomor_baptisan = fields.Char(
        string="Nomor Surat Baptisan"
    )
    tanggal_baptis = fields.Date(
        string="Tanggal Baptis"
    )
    dibaptis_oleh = fields.Many2one(
        string="Dibaptis oleh",
        comodel_name='gkr.anggota',
        domain=[('jabatan', '=', 'hamba_tuhan_pdt')]
    )

    """Data Meninggal"""
    tanggal_meninggal = fields.Datetime('Tanggal Meninggal')
    pemakaman = fields.Selection([
        ('kubur', 'Kubur'),
        ('kremasi', 'Kremasi')
    ], string='Pemakaman',
       default='kubur')
    
    rumah_duka_id = fields.Many2one(
        string='Rumah Duka',
        comodel_name='gkr.rumah.duka',
    )
    
    lokasi_penguburan_id = fields.Many2one(
        string='Lokasi Pemakaman',
        comodel_name='gkr.tempat.pemakaman'
    )
    lokasi_kremasi_id = fields.Many2one(
        string='Lokasi Kremasi',
        comodel_name='gkr.tempat.kremasi'
    )

    """Data Keluarga"""
    ayah = fields.Many2one(
        string='Ayah',
        comodel_name='gkr.anggota',
        domain=[('jenis_kelamin', '=', 'L')]
    )

    ibu = fields.Many2one(
        string='Ibu',
        comodel_name='gkr.anggota',
        domain=[('jenis_kelamin', '=', 'P')]
    )

    suami_id = fields.Many2one(
        string='Suami',
        comodel_name='gkr.anggota',
        domain=[('jenis_kelamin', '=', 'L')]
    )

    istri_id = fields.Many2one(
        string='Istri',
        comodel_name='gkr.anggota',
        domain=[('jenis_kelamin', '=', 'P')]
    )
    
    anak_ids = fields.Many2many(
        string='Anak',
        comodel_name='gkr.anggota',
        relation='relational_table_anak',
        column1='orang_tua',
        column2='anak',
        compute='_compute_anak'
    )

    saudara_ids = fields.Many2many(
        string='Saudara',
        comodel_name='gkr.anggota',
        relation='relational_table_saudara',
        column1='saya',
        column2='saudara',
        compute='_compute_saudara'
    )

    @api.depends('ayah','ibu')
    def _compute_saudara(self):
        saudara = self.env['gkr.anggota'].search([
            ('ayah', '=', self.ayah.id),
            ('ibu', '=', self.ibu.id),
            ('ayah', '!=', False),
            ('ibu', '!=', False)
        ])
        self.saudara_ids = [(4, s.id) if s.id != self.id else (4, 0) for s in saudara]

    @api.depends('suami_id', 'istri_id')
    def _compute_anak(self):
        if self.jenis_kelamin == 'L':
            anak = self.env['gkr.anggota'].search(['&',('ayah', '=', self.id), ('ibu', '=', self.istri_id.id)])
        else:
            anak = self.env['gkr.anggota'].search(['&',('ayah', '=', self.suami_id.id), ('ibu', '=', self.id)])
        self.anak_ids = [(4, a.id) if a.id != self.id else (4, 0) for a in anak]
    
    def write(self, values):
        
        result = super(Anggota, self).write(values)
    
        return result
    
    def whatsapp(self):
        number = str(self.no_telpon)
        trimmed_number = number[1:]
        final_number = "+62" + trimmed_number
        return {                   
            'name'     : 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : '_blank',
            'url'      : 'https://wa.me/'+ final_number
        }
    
    '''Foto dkk'''
    foto_ids = fields.One2many(
        comodel_name='gkr.foto', 
        inverse_name='anggota_id', 
        string='Foto lainnya')
    

class AnggotaLines(models.Model):
    _name = 'gkr.anggota.lines'
    _description = 'anggota_lines'

    anggota_id = fields.Many2one(
        'gkr.anggota', 
        string='Nama')
    
    hubungan = fields.Selection([
        ('anak', 'Anak'),
        ('saudara_kandung', 'Saudara Kandung'),
        ('orang_tua', 'Orang Tua'),
        ('pasangan', 'Pasangan')
    ], string='Hubungan')

class Gereja(models.Model):
    _name = 'gkr.gereja'
    name = fields.Char(
        string='Nama',
    )

    alamat = fields.Char(
        string='Alamat'
    )

class TempatPemakanam(models.Model):
    _name = 'gkr.tempat.pemakaman'
    name = fields.Char(
        string='Nama',
    )

    alamat = fields.Char(
        string='Alamat'
    )

class TempatKremasi(models.Model):
    _name = 'gkr.tempat.kremasi'
    name = fields.Char(
        string='Nama',
    )

    alamat = fields.Char(
        string='Alamat'
    )    

class RumahDuka(models.Model):
    _name = 'gkr.rumah.duka'
    name = fields.Char(
        string='Nama',
    )

    alamat = fields.Char(
        string='Alamat'
    )

class Foto(models.Model):
    _name = 'gkr.foto'
    name = fields.Char(string='Nama Foto')
    anggota_id = fields.Many2one('gkr.anggota', string='anggota')
    foto = fields.Binary(string='Foto')
    
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
    tanggal_lahir = fields.Date(
        string='Tanggal Lahir'
    )
    jenis_kelamin = fields.Selection([
        ('L', 'Laki-Laki'),
        ('P', 'Perempuan')
    ], string='Jenis Kelamin')

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
            ]
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
    gereja_asal = fields.Char(string='Gereja Asal')
    
    atestasi_keluar = fields.Boolean(string='Atestasi Keluar')
    tanggal_atestasi_keluar = fields.Date(
        string='Tanggal Keluar',
        default=fields.Date.context_today,
    )
    gereja_tujuan = fields.Char(string='Gereja Tujuan')

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
    ], string='Pemakaman')
    lokasi_penguburan = fields.Char(
        string='Lokasi Penguburan'
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

    pasangan_id = fields.Many2one(
        string='Pasangan',
        comodel_name='gkr.anggota',
        domain=lambda self: self._compute_pasangan_domain()
    )

    @api.depends('jenis_kelamin')
    def _compute_pasangan_domain(self):
        for record in self:
            if record.jenis_kelamin == 'L':
                domain = [('jenis_kelamin', '=', 'P')]
            else:
                domain = [('jenis_kelamin', '=', 'L')]
            return domain


    
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

    @api.depends('pasangan_id')
    def _compute_anak(self):
        if self.jenis_kelamin == 'L':
            anak = self.env['gkr.anggota'].search(['&',('ayah', '=', self.id), ('ibu', '=', self.pasangan_id.id)])
        else:
            anak = self.env['gkr.anggota'].search(['&',('ayah', '=', self.pasangan_id.id), ('ibu', '=', self.id)])
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
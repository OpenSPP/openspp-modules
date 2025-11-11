from odoo import models, fields, api

class TranslationWizard(models.TransientModel):
    _name = 'translation.wizard'
    _description = 'AI-Assisted Translation Wizard'

    source_text = fields.Text("Source Text", required=True)
    translated_text = fields.Text("Translated Text")

    @api.model
    def translate_text(self):
        # Simple placeholder logic (we fake translation for now)
        self.translated_text = f"TRANSLATED: {self.source_text}"

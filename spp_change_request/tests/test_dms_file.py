import base64

from odoo.tests import TransactionCase


class SPPDMSFileCustomTest(TransactionCase):
    def setUp(self):
        super().setUp()
        directory_id = self.env["dms.directory"].create(
            {
                "storage_id": self.env.ref(
                    "spp_change_request.dms_change_request_storage"
                ).id,
                "is_root_directory": True,
                "name": "test123directory",
                "res_model": "spp.change.request",
            }
        )

        content = """iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIf
            AhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d
            3Lmlua3NjYX
            BlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ
            /M7ubXdtdb1xSFyeilBapySVU8h8OoFaooF
            qiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFj
            nAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnW
            b2e/u992bee7tCa00YFsffekFY
            +nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3
            pdhOqLtYPHChahZcYYO7KvPFx
            vRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt
            2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeW
            pdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8X
            xt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihM
            sOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus
            96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsr
            HMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8Qyqw
            Z+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlw
            jlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8
            R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428
            m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2v
            c/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59o
            WVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2re
            Ny1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFx
            Ikd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3dd
            aHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1w
            i/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCo
            hX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UA
            AAAASUVORK5CYII=
        """
        content = content.replace(" ", "").replace("\n", "")
        content = bytes(content, "utf-8")
        dms_file_vals = {
            "directory_id": directory_id.id,
            "name": "Test File Name",
            "content": base64.b64encode(content),
        }
        self._dms_file = self.env["dms.file"].create(dms_file_vals)

    def test_01_action_save_and_close(self):
        action = self._dms_file.action_save_and_close()
        self.assertEqual(action.get("type"), "ir.actions.act_window_close")

    def test_02_action_attach_documents(self):
        action = self._dms_file.action_attach_documents()
        self.assertEqual(action.get("type"), "ir.actions.act_window")

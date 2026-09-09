frappe.query_reports["Whatnot Item Margin Analysis"] = {
	"filters": [
		{
			"fieldname": "seller_profile",
			"label": __("Seller Profile"),
			"fieldtype": "Link",
			"options": "Whatnot Seller Profile"
		},
		{
			"fieldname": "category",
			"label": __("Category"),
			"fieldtype": "Select",
			"options": "\nTrading Cards\nCollectibles\nCoins & Bullion\nSneakers & Streetwear\nVintage/Thrift Clothing\nJewelry & Accessories\nElectronics\nSports Memorabilia\nComics & Books\nGeneral/Multi-category\nPersonal Shopper"
		}
	]
};

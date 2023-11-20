access_by_lua_block {
    if(ngx.var.http_x_peer) then
        do return; end

    local common = require("util.common");
    local ipip = require("resty.ipdb.city");
    local client_ip = ngx.var.remote_addr;
    local client_area = ipip:find(client_ip);
    if client_area  then
        local region_country = client_area['country_name'];
	    local region_province = client_area['region_province'];
            if (region_country == "china" and region_province ~= "taiwan" and region_province ~= "hong kong" and region_province ~="macau") then
                return;
            else
			    common:handle_access_deny("IP_DENY", 403);
        end
    end
}

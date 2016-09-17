$(document).ready(function () {

    var $constants = $('#gargoyle-constants'),
        urls = {
            addSwitch: $constants.data('urlAddSwitch'),
            updateSwitch: $constants.data('urlUpdateSwitch'),
            deleteSwitch: $constants.data('urlDeleteSwitch'),
            updateStatus: $constants.data('urlUpdateStatus'),
            addCondition: $constants.data('urlAddCondition'),
            removeCondition: $constants.data('urlRemoveCondition'),
            deleteImage: $constants.data('urlDeleteImage')
        },
        api = function (url, params, succ) {
            $('#status').show();
            $.ajax({
                url: url,
                type: "POST",
                data: params,
                dataType: "json",
                success: function (resp) {
                    $('#status').hide();

                    if (resp.success) {
                        succ(resp.data);
                    } else {
                        alert(resp.data);
                    }
                },
                failure: function() {
                    $('#status').hide();
                    alert('There was an internal error. Data probably wasn\'t saved');
                }
            });
        };
        switchFormTemplate = $.templates('#switchForm'),
        switchDataTemplate = $.templates('#switchData'),
        switchConditionsTemplate = $.templates('#switchConditions');

    $.views.settings.allowCode(true);

    // Events

    $(".addSwitch").click(function (ev) {
        ev.preventDefault();
        var content = switchFormTemplate.render({ add: true });
        $.facebox(content);
    });

    $(".switches .edit").live("click", function () {
        var row = $(this).parents("tr:first"),
            content = switchFormTemplate.render({
                add:    false,
                curkey: row.data("switchKey"),
                key:    row.data("switchKey"),
                name:   row.data("switchName"),
                desc:   row.data("switchDesc")
            });

        $.facebox(content);
    });

    $(".switches .delete").live("click", function () {
        var row = $(this).parents("tr:first");
        var table = row.parents("table:first");

        if (!confirm('Are you SURE you want to remove this switch?')) {
            return;
        }

        api(urls.deleteSwitch, { key: row.data("switchKey") },
            function () {
                row.remove();
                if (!table.find("tr").length) {
                    $("div.noSwitches").show();
                }
            });
    });

    $(".switches td.status button").live("click", function () {
        var row = $(this).parents("tr:first");
        var el = $(this);
        var status = el.data("status");
        var labels = {
            4: "(Inherit from parent)",
            3: "(Active for everyone)",
            2: "(Active for conditions)",
            1: "(Disabled for everyone)"
        };

        if (status == 3) {
            if (!confirm('Are you SURE you want to enable this switch globally?')) {
                return;
            }
        }

        api(urls.updateStatus,
            {
                key:    row.data('switchKey'),
                status: status
            },

            function (swtch) {
                if (swtch.status == status) {
                    row.find(".toggled").removeClass("toggled");
                    el.addClass("toggled");
                    row.data('switchStatus', swtch.status);
                    if ($.isArray(swtch.conditions) && swtch.conditions.length < 1 && swtch.status == 2) {
                        swtch.status = 3;
                    }
                    row.find('.status p').text(labels[swtch.status]);
                }
            });
    });

    $("p.addCondition a").live("click", function (ev) {
        ev.preventDefault();
        var form = $(this).parents("td:first").find("div.conditionsForm:first"),
            content;

        if (form.is(":hidden")) {
            content = switchConditionsTemplate.render({});
            form.html(content);
            form.addClass('visible');
        } else {
            form.removeClass('visible');
        }
    });

    $("div.conditionsForm select").live("change", function () {
        var field = $(this).val().split(",");
        $(this).
            parents("tr:first").
            find("div.fields").hide();

        $(this).
            parents("tr:first").
            find("div[data-path='" + field[0] + "." + field[1] + "']").show();
    });

    $("div.conditionsForm form").live("submit", function (ev) {
        ev.preventDefault();

        var data = {
            key: $(this).parents("tr:first").data('switchKey'),
            id: $(this).data('switch'),
            field: $(this).data('field')
        };

        $.each($(this).find("input"), function () {
            var val;

            if ($(this).attr('type') == 'checkbox') {
                val = $(this).is(':checked') ? '1' : '0';
            } else {
                val = $(this).val();
            }
            data[$(this).attr("name")] = val;
        });

        api(urls.addCondition, data, function (swtch) {
            var content = switchDataTemplate.render(swtch);
            $("table.switches tr[data-switch-key='"+ data.key + "']").replaceWith(content);
        });
    });

    $("div.conditions span.value a.delete-condition").live("click", function (ev) {
        ev.preventDefault();

        var el = $(this).parents("span:first"),
            data = {
                key:   el.parents("tr:first").data('switchKey'),
                id:    el.data('switch'),
                field: el.data('field'),
                value: el.data('value')
            };

        api(urls.removeCondition, data, function (swtch) {
            var content = switchDataTemplate.render(swtch);
            $("table.switches tr[data-switch-key='"+ data.key + "']").replaceWith(content);
        });

    });

    $("#facebox .closeFacebox").live("click", function (ev) {
        ev.preventDefault();
        $.facebox.close();
    });

    $("#facebox .submitSwitch").live("click", function () {
        var action = $(this).data('action'),
            curkey = $(this).data('curkey');

        api(action == "add" ? urls.addSwitch : urls.updateSwitch,
            {
                curkey: curkey,
                name:   $("#facebox input[name=name]").val(),
                key:    $("#facebox input[name=key]").val(),
                desc:   $("#facebox textarea").val()
            },

            function (swtch) {
                var content = $(switchDataTemplate.render(swtch));

                if (action == "add") {
                    if ($("table.switches tr").length === 0) {
                        $("table.switches").html(content);
                        $("table.switches").removeClass("empty");
                        $("div.noSwitches").hide();
                    } else {
                        $("table.switches tr:last").after(content);
                    }

                    $.facebox.close();
                } else {
                    $("table.switches tr[data-switch-key='" + curkey + "']").replaceWith(content);
                    $.facebox.close();
                }
                content.click();
            }
        );
    });

    $('.search input').keyup(function () {
        var query = $(this).val();
        $('.switches tr').removeClass('hidden');
        if (!query) {
            return;
        }
        $('.switches tr').each(function (_, el) {
            var $el = $(el);
            var score = 0;
            score += $el.data('switchKey').score(query);
            score += $el.data('switchName').score(query);
            if ($el.data('switchDescription')) {
                score += $el.data('switchDescription').score(query);
            }
            if (score === 0) {
                $el.addClass('hidden');
            }
        });
    });
});

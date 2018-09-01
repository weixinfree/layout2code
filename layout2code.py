#!/usr/bin/env python3

import os
import re
from typing import List
from xml.etree.ElementTree import ElementTree, Element


class Item:
    def __init__(self):
        self.node = None
        self.index = 0
        self.tag = ''
        self.attrs = {}
        self.level = 0
        self.parent = None
        self.name = ''

    def __repr__(self):
        return f'Item(tag={self.tag}, level={self.level}, name={self.name}, parent={self.parent})'


class View:
    def __init__(self):
        self._indent = ''

    def indent(self, level: int):
        self._indent = level * 4 * ' '

    def comment(self, item: Item) -> str:
        return self._indent + f"// view: {item.tag}"

    def view(self, item: Item) -> str:
        return self._indent + f'{item.tag} {item.name} = new {item.tag}(context);'

    def visibility(self, value: str, item: Item) -> str:
        return self._indent + f'{item.name}.setVisibility(View.{value.upper()});'

    def view_params(self, item: Item):
        if item.parent:
            return self._indent + f'{item.parent.tag}.LayoutParams {item.name}_params = new {item.parent.tag}.LayoutParams(0, 0);'
        else:
            return self._indent + f'ViewGroup.LayoutParams {item.name}_params = new ViewGroup.LayoutParams(0, 0);'

    def color(self, value: str) -> str:
        m = re.match(r'@color/(\w+)', value)
        if m:
            return f'ContextCompat.getColor(context, R.color.{m.group(1)})'

        m = re.match('#([0-9a-fA-F]+)', value)
        if m:
            return f"Color.parseColor(\"{value}\")"

        return value

    def enabled(self, value: str, item: Item):
        return self._indent + f'{item.name}.setEnabled({value});'

    def progress(self, value: str, item: Item):
        return self._indent + f'{item.name}.setProgress({value});'

    def alpha(self, value:str, item: Item):
        return self._indent + f'{item.name}.setAlpha({value});'

    def includeFontPadding(self, value: str, item: Item):
        return self._indent + f'{item.name}.setIncludeFontPadding({value});'

    def id_res(self, value: str) -> str:
        return 'R.id.' + re.match(r'@\+?id/(\w+)', value).group(1)

    def dimen(self, value: str) -> str:
        if value == 'wrap_content':
            return 'ViewGroup.LayoutParams.WRAP_CONTENT'

        if value == 'match_parent':
            return 'ViewGroup.LayoutParams.MATCH_PARENT'

        m = re.match('([\d.]+)dp', value)
        if m:
            return f'DisplayUtil.dip2px(context, {m.group(1)}F)'

        m = re.match('([\d.]+)dip', value)
        if m:
            return f'DisplayUtil.dip2px(context, {m.group(1)}F)'

        m = re.match('([\d.]+)sp', value)
        if m:
            return f'DisplayUtil.sp2px(context, {m.group(1)}F)'

        m = re.match('(\d+)px', value)
        if m:
            return f'{m.group(1)}'

        m = re.match(r'@dimen/dimens_dip_(\d+)', value)
        if m:
            return f'DisplayUtil.dip2px(context, {m.group(1)}F)'

        m = re.match(r'@dimen/dimens_sp_(\d+)', value)
        if m:
            return f'DisplayUtil.sp2px(context, {m.group(1)}F)'

        return value

    def layout_width(self, value, item: Item):
        return self._indent + f'{item.name}_params.width = {self.dimen(value)};'

    def layout_height(self, value, item: Item):
        return self._indent + f'{item.name}_params.height = {self.dimen(value)};'

    def layout_alignParentLeft(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_PARENT_LEFT);'

    def layout_alignParentBottom(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_PARENT_BOTTOM);'

    def layout_alignParentTop(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_PARENT_TOP);'

    def layout_alignParentRight(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_PARENT_RIGHT);'

    def orientation(self, value: str, item: Item):
        return self._indent + f'{item.name}.setOrientation(LinearLayout.{value.upper()});'

    def gravity(self, value: str, item: Item):
        return self._indent + f"{item.name}.setGravity(Gravity.{value.upper()});"

    def layout_marginBottom(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.bottomMargin = {self.dimen(value)};'

    def layout_marginLeft(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.leftMargin = {self.dimen(value)};'

    def layout_marginRight(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.rightMargin = {self.dimen(value)};'

    def textStyle(self, value: str, item: Item):
        return self._indent + f'{item.name}.setTypeface(null, Typeface.BOLD);'

    def layout_marginTop(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.topMargin = {self.dimen(value)};'

    def layout_alignBottom(self, value: str, item: Item):
        m = re.match(r'@\+?id/(\w+)', value)
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_BOTTOM, R.id.{m.group(1)});'

    def layout_alignTop(self, value: str, item: Item):
        m = re.match(r'@\+?id/(\w+)', value)
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_TOP, R.id.{m.group(1)});'

    def layout_alignRight(self, value: str, item: Item):
        m = re.match(r'@\+?id/(\w+)', value)
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_RIGHT, R.id.{m.group(1)});'

    def layout_alignLeft(self, value: str, item: Item):
        m = re.match(r'@\+?id/(\w+)', value)
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.ALIGN_LEFT, R.id.{m.group(1)});'

    # def TextView_style(self, value: str, item: Item):
    #     m = re.match(r'@style/(.+)', value)
    #     return f'{self._indent}if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {{\n{self._indent}\t{item.name}.setTextAppearance(R.style.{"_".join(m.group(1).split("."))});\n{self._indent}}}'

    def layout_below(self, value: str, item: Item):
        m = re.match(r'@\+?id/(\w+)', value)
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.BELOW, R.id.{m.group(1)});'

    def clickable(self, value: str, item: Item):
        return self._indent + f'{item.name}.setClickable({value});'

    def ViewStub_layout(self, value: str, item: Item):
        m = re.match(r'@layout/(\w+)', value)
        return self._indent + f'{item.name}.setLayoutResource(R.layout.{m.group(1)});'

    def ViewStub_inflatedId(self, value: str, item: Item):
        m = re.match("@\+?id/(\w+)", value)
        return self._indent + f'{item.name}.setInflatedId(R.id.{m.group(1)});'

    def minWidth(self, value: str, item: Item):
        return self._indent + f'{item.name}.setMinimumWidth({self.dimen(value)});'

    def minHeight(self, value: str, item: Item):
        return self._indent + f'{item.name}.setMinimumHeight({self.dimen(value)});'

    def layout_gravity(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.gravity = Gravity.{value.upper()};'

    def background(self, value: str, item: Item):
        m = re.match('@color/(\w+)', value)
        if m:
            return self._indent + f'{item.name}.setBackgroundColor(ContextCompat.getColor(context, R.color.{m.group(1)}));'

        m = re.match(r'@drawable/(\w+)', value)
        return self._indent + f'{item.name}.setBackgroundResource(R.drawable.{m.group(1)});'

    def src(self, value: str, item: Item):
        return self._indent + f'{item.name}.setImageResource({self._drawable(value)});'

    def singleLine(self, value: str, item: Item):
        return self._indent + f'{item.name}.setSingleLine(true);'

    def scaleType(self, value: str, item: Item):
        types = {
            'centerCrop': "CENTER_CROP",
            'fitXY': 'FIT_XY',
            'centerInside': 'CENTER_INSIDE',
            'fitCenter':'FIT_CENTER'
        }
        return self._indent + f'{item.name}.setScaleType(ImageView.ScaleType.{types[value]});'

    shadowMark = set()

    def shadowColor(self, value: str, item: Item):

        if item in View.shadowMark:
            return ''

        View.shadowMark.add(item)

        dx = item.attrs.get('shadowDx', 0)
        dy = item.attrs.get('shadowDy', 0)
        radius = item.attrs.get('shadowRadius', 0)
        color = item.attrs.get('shadowColor', '')

        return self._indent + f'{item.name}.setShadowLayer({radius}F, {dx}F, {dy}F, {self.color(color)});'

    shadowDx = shadowColor
    shadowDy = shadowColor
    shadowRadius = shadowColor

    paddingMark = set()

    def paddingBottom(self, value: str, item: Item):

        if item in View.paddingMark:
            return self._indent

        View.paddingMark.add(item)

        left = item.attrs.get('paddingLeft', '0dp')
        top = item.attrs.get('paddingTop', '0dp')
        right = item.attrs.get('paddingRight', '0dp')
        bottom = item.attrs.get('paddingBottom', '0dp')
        return self._indent + f'{item.name}.setPadding({self.dimen(left)}, {self.dimen(top)}, {self.dimen(right)}, {self.dimen(bottom)});'

    paddingTop = paddingBottom
    paddingLeft = paddingBottom
    paddingRight = paddingBottom

    def TextView_maxLines(self, value: str, item: Item):
        return self._indent + f'{item.name}.setMaxLines({value});'

    def lineSpacingExtra(self, value: str, item: Item):
        return self._indent + f'{item.name}.setLineSpacing({self.dimen(value)}, {item.name}.getLineSpacingMultiplier());'

    def ellipsize(self, value: str, item: Item):
        if value == 'none':
            return self._indent

        return self._indent + f'{item.name}.setEllipsize(TextUtils.TruncateAt.{value.upper()});'

    def TextView_maxLength(self, value: str, item: Item):
        return self._indent + f'enter_room_nick.setFilters(new InputFilter[] {{ new InputFilter.LengthFilter({value}) }});'

    def id(self, value, item: Item):
        _id = re.match(r'@\+?id/(.*)', value).group(1)
        return self._indent + f'{item.name}.setId(R.id.{_id});'

    def textColor(self, value: str, item: Item):
        return self._indent + f'{item.name}.setTextColor({self.color(value)});'

    def textSize(self, value: str, item: Item):
        return self._indent + f'{item.name}.setTextSize(TypedValue.COMPLEX_UNIT_PX, {self.dimen(value)});'

    def maxEms(self, value: str, item: Item):
        return self._indent + f'{item.name}.setMaxEms({value});'

    def layout_centerVertical(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.CENTER_VERTICAL);'

    def layout_centerHorizontal(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.CENTER_HORIZONTAL);'

    def layout_centerInParent(self, value:str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.CENTER_IN_PARENT);'

    def layout_toRightOf(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.RIGHT_OF, {self.id_res(value)});'

    def layout_toLeftOf(self, value: str, item: Item):
        return self._indent + f'{item.name}_params.addRule(RelativeLayout.LEFT_OF, {self.id_res(value)});'

    def _str(self, value: str) -> str:
        m = re.match('@string/(\w+)', value)
        if m:
            return 'R.string.' + m.group(1)

        return f'"{value}"'

    def text(self, value: str, item: Item):
        return self._indent + f'{item.name}.setText({self._str(value)});'

    def TextView_maxWidth(self, value: str, item: Item):
        return self._indent + f'{item.name}.setMaxWidth({self.dimen(value)});'

    draweeMark = set()

    def roundAsCircle(self, value: str, item: Item):
        """{
            final GenericDraweeHierarchyBuilder builder = new GenericDraweeHierarchyBuilder(context.getResources());
            final RoundingParams roundingParams = new RoundingParams();
            roundingParams.setRoundAsCircle(true);
            builder.setRoundingParams(roundingParams);
            img_barrage_auth.setHierarchy(builder.build());
        }
        """

        if item in View.draweeMark:
            return self._indent

        View.draweeMark.add(item)

        inner_indent = self._indent + ' ' * 4

        result = []
        result.append(self._indent + '{')
        result.append(
            inner_indent + 'final GenericDraweeHierarchyBuilder builder = new GenericDraweeHierarchyBuilder(context.getResources());')

        if 'placeholderImage' in item.attrs:
            image = item.attrs['placeholderImage']
            result.append(inner_indent + f'builder.setPlaceholderImage({self._drawable(image)});')

        if 'failureImage' in item.attrs:
            image_ = item.attrs['failureImage']
            result.append(inner_indent + f'builder.setFailureImage({self._drawable(image_)});')

        if 'placeholderImageScaleType' in item.attrs:
            type = item.attrs['placeholderImageScaleType']
            types = {'fitXY': 'FIT_XY', 'fitCenter':'FIT_CENTER'}
            result.append(inner_indent + f'builder.setPlaceholderImageScaleType(ScalingUtils.ScaleType.{types[type]});')

        if 'failureImageScaleType' in item.attrs:
            type = item.attrs['failureImageScaleType']
            types = {'fitXY': 'FIT_XY', 'fitCenter': 'FIT_CENTER'}
            result.append(inner_indent + f'builder.setFailureImageScaleType(ScalingUtils.ScaleType.{types[type]});')

        if 'actualImageScaleType' in item.attrs:
            type = item.attrs['actualImageScaleType']
            types = {'fitXY': 'FIT_XY', 'fitCenter': 'FIT_CENTER'}
            result.append(inner_indent + f'builder.setActualImageScaleType(ScalingUtils.ScaleType.{types[type]});')

        if 'fadeDuration' in item.attrs:
            duration_ = item.attrs['fadeDuration']
            result.append(inner_indent + f'builder.setFadeDuration({duration_});')


        result.append(inner_indent + 'final RoundingParams roundingParams = new RoundingParams();')

        if 'roundAsCircle' in item.attrs:
            as_circle_ = item.attrs['roundAsCircle']
            result.append(inner_indent + f'roundingParams.setRoundAsCircle({as_circle_});')

        if 'roundingBorderColor' in item.attrs:
            color = item.attrs['roundingBorderColor']
            result.append(inner_indent + f'roundingParams.setBorderColor({self.color(color)});')

        if 'roundingBorderWidth' in item.attrs:
            width_ = item.attrs['roundingBorderWidth']
            result.append(inner_indent + f'roundingParams.setBorderWidth({self.dimen(width_)});')

        result.append(inner_indent + 'builder.setRoundingParams(roundingParams);')
        result.append(inner_indent + f'{item.name}.setHierarchy(builder.build());')

        result.append(self._indent + '}')

        return '\n'.join(result)

    placeholderImage = roundAsCircle
    fadeDuration = roundAsCircle
    roundingBorderColor = roundAsCircle
    roundingBorderWidth = roundAsCircle
    placeholderImageScaleType = roundAsCircle
    failureImage = roundAsCircle
    failureImageScaleType = roundAsCircle
    actualImageScaleType = roundAsCircle


    def _drawable(self, value: str) -> str:
        return 'R.drawable.' + re.match(r'@drawable/(\w+)', value).group(1)

    def attr(self, attr: str, value: str, item: Item):
        tag = item.tag.split('.')[-1]
        if hasattr(self, f'{tag}_{attr}'):
            return getattr(self, f'{tag}_{attr}')(value, item)

        if hasattr(self, attr):
            return getattr(self, attr)(value, item)

        return self._indent + f'// TODO: 无法处理的属性: {attr}={value}'

    def end(self, item: Item):
        if item.parent:
            return self._indent + f'{item.parent.name}.addView({item.name}, {item.name}_params);'
        else:
            return self._indent + f'$root.addView({item.name}, {item.name}_params);'


view = View()


def _gen_code(item: Item, code: List):
    indent = 2
    view.indent(indent)
    code.append('')
    code.append(view.comment(item))
    code.append(view.view(item))

    for attr, value in item.attrs.items():
        if 'layout' not in attr:
            code.append(indent * 4 * ' ' + f'// {attr} = {value}')
            code.append(view.attr(attr, value, item))

    layout = item.tag.split('.')[-1] + '_params'
    if hasattr(view, layout):
        code.append(getattr(view, layout)(item))
    else:
        code.append(view.view_params(item))

    for attr, value in item.attrs.items():
        if 'layout' in attr:
            code.append(indent * 4 * ' ' + f'// {attr} = {value}')
            code.append(view.attr(attr, value, item))

    code.append(view.end(item))


def _gen_name(item: Item):
    if 'id' in item.attrs:
        return item.attrs['id'].split('/')[-1]

    base = item.parent.name if item.parent else ''
    return 'p_' + base + '_child_' + str(item.index)


def _visit_tree(root: Element, f, level: int = 0, index: int = 0, parent: Item = None):
    item = Item()
    item.node = root
    item.index = index
    item.tag = root.tag
    item.attrs = {re.sub(r'\{.*?\}', '', k).strip(): v for k, v in root.attrib.items()}
    item.level = level
    item.parent = parent if parent else None
    item.name = _gen_name(item)

    f(item)

    children = list(root)
    if children:
        for index, child in enumerate(children):
            _visit_tree(child, f, level + 1, index, item)


def file_2_java_class_name(file: str) -> str:
    return ''.join([part.title() for part in os.path.basename(file)[:-4].split('_')])


def layout2code(file: str):
    tree = ElementTree(file=file)
    root = tree.getroot()

    code = ['final Context context = $root.getContext();']

    rootItem: Item = None

    def capture_root(item: Item):
        nonlocal rootItem
        if not rootItem:
            rootItem = item

        _gen_code(item, code)

    _visit_tree(root, capture_root)
    code.append(f'return {rootItem.name};')
    code = '\n'.join(code)

    result = f'''\

import android.content.Context;

import android.support.v4.content.ContextCompat;
import android.text.InputFilter;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;

import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.TextView;

import com.facebook.drawee.generic.GenericDraweeHierarchyBuilder;
import com.facebook.drawee.generic.RoundingParams;
import com.*.utils.DisplayUtil;

/**
 * {os.path.basename(file)}
 */
public class R_Layout_{os.path.basename(file)[:-4]} {{

    public static View inflate(ViewGroup $root) {{
        {code}
    }}
}}
'''
    print(result)


if __name__ == '__main__':
    import fire

    fire.Fire(layout2code)

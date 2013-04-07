Summary:	Asynchronous JavaScript Engine
Name:		nodejs
Version:	0.10.3
Release:	3
License:	BSD and MIT and Apache v2.0 and GPL v3
Group:		Development/Languages
Source0:	http://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz
# Source0-md5:	4daca92618515708a4631e98a8e8c779
Patch1:		%{name}-shared.patch
# force node to use /usr/lib/node as the systemwide module directory
Patch2:		%{name}-libpath.patch
# use /usr/lib64/node as an arch-specific module dir when appropriate
Patch3:		%{name}-lib64path.patch
Patch5:		uv-fpic.patch
URL:		http://www.nodejs.org/
BuildRequires:	c-ares-devel
BuildRequires:	gcc >= 5:4.0
BuildRequires:	libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	python >= 1:2.5.2
BuildRequires:	python-jsmin
BuildRequires:	rpm >= 4.4.9-56
BuildRequires:	rpmbuild(macros) >= 1.219
BuildRequires:	v8-devel >= 3.15.11.10
BuildRequires:	zlib-devel
BuildConflicts:	eio
Obsoletes:	nodejs-waf
ExclusiveArch:	%{ix86} %{x8664} arm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Node.js is a platform built on Chrome's JavaScript runtime for easily
building fast, scalable network applications. Node.js uses an
event-driven, non-blocking I/O model that makes it lightweight and
efficient, perfect for data-intensive real-time applications that run
across distributed devices.

%package devel
Summary:	Development headers for nodejs
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	gcc
Requires:	libstdc++-devel
Requires:	v8-devel

%description devel
Development headers for nodejs.

%package doc
Summary:	Evented I/O for V8 JavaScript - documentation
Group:		Documentation

%description doc
Node.js is a server-side JavaScript environment that uses an
asynchronous event-driven model. Node's goal is to provide an easy way
to build scalable network programs.

This package contains the documentation for nodejs.

%prep
%setup -q -n node-v%{version}
%patch1 -p1
%if %{_lib} == "lib64"
%patch3 -p1
%else
%patch2 -p1
%endif
%patch5 -p1

%build
# Error: V8 doesn't like ccache. Please set your CC env var to 'gcc'
CC=${CC#ccache }

# NOT autoconf so dont use macro
export PYTHONPATH=tools
./configure \
	--shared-v8 \
	--shared-zlib \
	--shared-openssl \
	--shared-cares \
	--without-npm \
	--without-dtrace \
	--prefix=%{_prefix}

%{__make} -C out \
	BUILDTYPE=Release \
	V=1 \
	CFLAGS.host="%{rpmcflags} -fPIC" \
	CXXFLAGS.host="%{rpmcppflags} -fPIC" \
	LDFLAGS.host="%{rpmcflags}" \
	CFLAGS.target="%{rpmcflags} -fPIC" \
	CXXFLAGS.target="%{rpmcppflags} -fPIC" \
	LDFLAGS.target="%{rpmcflags}" \
	CC.host="%{__cc}" \
	CXX.host="%{__cxx}" \
	CC.target="%{__cc}" \
	CXX.target="%{__cxx}"

%install
rm -rf $RPM_BUILD_ROOT
%{__make} justinstall \
	DESTDIR=$RPM_BUILD_ROOT \
	LIBDIR=%{_lib}

# no dtrace on linux
%{__rm} -r $RPM_BUILD_ROOT%{_prefix}/lib/dtrace/node.d

lib=$(basename $RPM_BUILD_ROOT%{_libdir}/libnode.so.*.*)
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libnode.so.10
ln -s $lib $RPM_BUILD_ROOT%{_libdir}/libnode.so

echo '.so man1/node.1' > $RPM_BUILD_ROOT%{_mandir}/man1/nodejs.1

install -d $RPM_BUILD_ROOT%{_includedir}/node
cp -p src/*.h $RPM_BUILD_ROOT%{_includedir}/node
cp -p deps/uv/include/uv.h $RPM_BUILD_ROOT%{_includedir}/node
cp -a deps/uv/include/uv-private $RPM_BUILD_ROOT%{_includedir}/node

# install for node-gyp
install -d $RPM_BUILD_ROOT%{_usrsrc}/%{name}
cp -p common.gypi $RPM_BUILD_ROOT%{_usrsrc}/%{name}
ln -s %{_includedir}/node $RPM_BUILD_ROOT%{_usrsrc}/%{name}/src

# for compat of fedora derivered scripts (shebangs)
ln -s node $RPM_BUILD_ROOT%{_bindir}/nodejs

# globally installed node modules (noarch)
install -d $RPM_BUILD_ROOT%{_prefix}/lib/node_modules

# default searchpaths
install -d $RPM_BUILD_ROOT{%{_libdir},%{_prefix}/lib}/node

# create pkgconfig
install -d $RPM_BUILD_ROOT%{_pkgconfigdir}
cat <<'EOF' > $RPM_BUILD_ROOT%{_pkgconfigdir}/%{name}.pc
version=%{version}
prefix=%{_prefix}
libdir=${prefix}/%{_lib}
includedir=${prefix}/include/node

Name: nodejs
Description: Evented I/O for V8 JavaScript.
Version: ${version}
Cflags: -I${includedir}
EOF

# install documentation
install -d $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
cp -a doc/api/* $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}
rm $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.markdown
rm $RPM_BUILD_ROOT%{_docdir}/%{name}-doc-%{version}/*.json

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md AUTHORS ChangeLog LICENSE
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/nodejs
%attr(755,root,root) %{_libdir}/libnode.so.*.*.*
%ghost %{_libdir}/libnode.so.10
%if "%{_lib}" != "lib"
%dir %{_libdir}/node
%endif
%dir %{_prefix}/lib/node
%dir %{_prefix}/lib/node_modules
%{_mandir}/man1/node.1*
%{_mandir}/man1/nodejs.1

%files devel
%defattr(644,root,root,755)
%{_libdir}/libnode.so
%{_includedir}/node
%{_pkgconfigdir}/nodejs.pc
%{_usrsrc}/%{name}

%files doc
%defattr(644,root,root,755)
%doc %{_docdir}/%{name}-doc-%{version}
